"""
Separation API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import logging
import asyncio

from app.core.database import get_db
from app.models.audio_file import AudioFile
from app.models.separation_job import SeparationJob, JobStatus
from app.schemas.separation import SeparationJobCreate, SeparationJobResponse
from app.workers.celery_worker import separate_audio_task

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/separate/{file_id}", response_model=SeparationJobResponse, status_code=202)
def create_separation_job(
    file_id: str,
    job_params: SeparationJobCreate,
    db: Session = Depends(get_db)
):
    """
    Start audio separation job
    Returns job information immediately, processing happens asynchronously
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

    # Start asynchronous processing
    separate_audio_task.delay(
        job_id=job.id,
        audio_file_path=audio_file.original_path,
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

    # Delete job directory (contains all separated tracks)
    from app.services.file_manager import file_manager
    from app.core.config import settings
    from pathlib import Path

    job_dir = Path(settings.TEMP_PATH) / job_id
    if job_dir.exists():
        file_manager.delete_directory(str(job_dir))

    # Delete from database
    db.delete(job)
    db.commit()

    logger.info(f"Deleted separation job: {job_id}")
    return None


@router.websocket("/jobs/{job_id}/ws")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job status updates
    """
    await websocket.accept()

    try:
        # Get database session
        db = next(get_db())

        while True:
            # Get current job status
            job = db.query(SeparationJob).filter(SeparationJob.id == job_id).first()

            if not job:
                await websocket.send_json({"error": "Job not found"})
                break

            # Send status update
            status_update = {
                "job_id": job.id,
                "status": job.status.value if isinstance(job.status, JobStatus) else job.status,
                "progress": job.progress,
                "error_message": job.error_message
            }

            await websocket.send_json(status_update)

            # If job is completed or failed, close connection
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED]:
                await websocket.close()
                break

            # Wait before next update
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for job {job_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()
    finally:
        db.close()
