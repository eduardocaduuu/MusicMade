"""
Celery worker for asynchronous audio processing tasks
"""
from celery import Celery, Task
from celery.signals import task_prerun, task_postrun
import logging
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.separation_job import SeparationJob, JobStatus
from app.models.track import Track
from app.services.separator import AudioSeparator
from app.services.file_manager import file_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery
celery_app = Celery(
    "musicmade",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    worker_prefetch_multiplier=1,  # One task at a time for memory efficiency
    worker_max_tasks_per_child=10,  # Restart worker after 10 tasks to free memory
)


class DatabaseTask(Task):
    """Base task with database session management"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = SessionLocal()
        return self._db

    def after_return(self, *args, **kwargs):
        if self._db is not None:
            self._db.close()
            self._db = None


@celery_app.task(bind=True, base=DatabaseTask)
def separate_audio_task(self, job_id: str, audio_file_path: str, algorithm: str, quality: str):
    """
    Celery task for audio separation
    """
    logger.info(f"Starting separation task for job {job_id}")

    db = self.db

    try:
        # Get job from database
        job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return {"status": "error", "message": "Job not found"}

        # Update job status to processing
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        job.progress = 0.0
        db.commit()

        # Create output directory for this job
        output_dir = file_manager.create_job_directory(job_id)

        # Progress callback to update database
        def update_progress(progress: float):
            job.progress = progress
            db.commit()
            self.update_state(state='PROGRESS', meta={'progress': progress})

        # Initialize separator
        separator = AudioSeparator(algorithm=algorithm)

        # Perform separation
        logger.info(f"Separating audio file: {audio_file_path}")
        separated_tracks = separator.separate_audio(
            audio_file_path,
            str(output_dir),
            progress_callback=update_progress
        )

        logger.info(f"Separation complete. Tracks: {list(separated_tracks.keys())}")

        # Save track information to database
        for instrument_name, track_path in separated_tracks.items():
            track_file = Path(track_path)
            if track_file.exists():
                # Get file size
                file_size = track_file.stat().st_size

                # Get duration using librosa
                import librosa
                duration = librosa.get_duration(path=str(track_file))

                # Create track record
                track = Track(
                    separation_job_id=job_id,
                    instrument_name=instrument_name,
                    file_path=str(track_path),
                    duration=float(duration),
                    file_size=file_size
                )
                db.add(track)

        # Update job to completed
        job.status = JobStatus.COMPLETED
        job.completed_at = datetime.utcnow()
        job.progress = 100.0
        db.commit()

        logger.info(f"Job {job_id} completed successfully")

        return {
            "status": "completed",
            "job_id": job_id,
            "tracks": list(separated_tracks.keys())
        }

    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}", exc_info=True)

        # Update job to failed
        try:
            job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()
            if job:
                job.status = JobStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.commit()
        except Exception as db_error:
            logger.error(f"Failed to update job status: {db_error}")

        return {
            "status": "failed",
            "job_id": job_id,
            "error": str(e)
        }


@celery_app.task
def cleanup_old_files(days: int = 7):
    """
    Cleanup old temporary files
    """
    logger.info(f"Starting cleanup of files older than {days} days")

    try:
        from datetime import timedelta
        import time

        current_time = time.time()
        cutoff_time = current_time - (days * 24 * 60 * 60)

        temp_path = Path(settings.TEMP_PATH)
        deleted_count = 0

        for item in temp_path.iterdir():
            if item.is_dir():
                # Check directory modification time
                if item.stat().st_mtime < cutoff_time:
                    file_manager.delete_directory(str(item))
                    deleted_count += 1
                    logger.info(f"Deleted old directory: {item}")

        logger.info(f"Cleanup complete. Deleted {deleted_count} directories")
        return {"deleted_count": deleted_count}

    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"error": str(e)}


# Periodic task to cleanup old files (if using celery beat)
celery_app.conf.beat_schedule = {
    'cleanup-old-files-daily': {
        'task': 'app.workers.celery_worker.cleanup_old_files',
        'schedule': 86400.0,  # Every 24 hours
        'args': (7,)  # Delete files older than 7 days
    },
}
