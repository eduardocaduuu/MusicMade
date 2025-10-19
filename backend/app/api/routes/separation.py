"""
Separation API endpoints - Simplified version without Celery
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging
from datetime import datetime
from pathlib import Path

from app.core.database import get_db
from app.models.audio_file import AudioFile
from app.models.separation_job import SeparationJob, JobStatus
from app.models.track import Track
from app.schemas.separation import SeparationJobCreate, SeparationJobResponse
from app.services.separator import AudioSeparator
from app.services.file_manager import file_manager

router = APIRouter()
logger = logging.getLogger(__name__)


def process_separation_sync(job_id: str, audio_path: str, algorithm: str, quality: str):
    """Process audio separation synchronously in background"""
    db = next(get_db())

    try:
        # Get job
        job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        # Update to processing
        job.status = JobStatus.PROCESSING
        job.started_at = datetime.utcnow()
        job.progress = 0.0
        db.commit()

        # Create output directory
        output_dir = file_manager.create_job_directory(job_id)

        # Progress callback
        def update_progress(progress: float):
            job.progress = progress
            db.commit()

        # Initialize separator
        separator = AudioSeparator(algorithm=algorithm)

        # Perform separation
        logger.info(f"Starting separation for job {job_id}")
        separated_tracks = separator.separate_audio(
            audio_path,
            str(output_dir),
            progress_callback=update_progress
        )

        logger.info(f"Separation complete. Tracks: {list(separated_tracks.keys())}")

        # Save tracks to database
        import librosa
        for instrument_name, track_path in separated_tracks.items():
            track_file = Path(track_path)
            if track_file.exists():
                file_size = track_file.stat().st_size
                duration = librosa.get_duration(path=str(track_file))

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

    finally:
        db.close()


@router.post("/separate/{file_id}", response_model=SeparationJobResponse, status_code=202)
def create_separation_job(
    file_id: str,
    job_params: SeparationJobCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start audio separation job (processes in background)
    Returns job information immediately
    """
    # Check if file exists
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()
    if not audio_file:
        raise HTTPException(status_code=404, detail="Audio file not found")

    # Create separation job
    job = SeparationJob(
        audio_file_id=file_id,
        algorithm=job_params.algorithm.value,
        quality=job_params.quality.value,
        status=JobStatus.PENDING
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Start background processing
    background_tasks.add_task(
        process_separation_sync,
        job_id=job.id,
        audio_path=audio_file.original_path,
        algorithm=job.algorithm,
        quality=job.quality
    )

    logger.info(f"Created separation job {job.id} for file {file_id}")

    return job


@router.get("/jobs/{job_id}", response_model=SeparationJobResponse)
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Get separation job status and results
    """
    job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job


@router.get("/jobs", response_model=List[SeparationJobResponse])
def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all separation jobs
    """
    jobs = db.query(SeparationJob).offset(skip).limit(limit).all()
    return jobs


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: str, db: Session = Depends(get_db)):
    """
    Delete a separation job and all associated tracks
    """
    job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Delete job directory
    from app.core.config import settings
    job_dir = Path(settings.TEMP_PATH) / job_id
    if job_dir.exists():
        file_manager.delete_directory(str(job_dir))

    # Delete from database
    db.delete(job)
    db.commit()

    logger.info(f"Deleted separation job: {job_id}")
    return None
