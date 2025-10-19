"""
Upload API endpoints
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.audio_file import AudioFile
from app.schemas.audio import AudioFileResponse
from app.services.file_manager import file_manager
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload", response_model=AudioFileResponse, status_code=201)
async def upload_audio_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file
    - Validates file format and size
    - Extracts metadata
    - Saves to database
    """
    try:
        # Validate file format
        if not file_manager.validate_audio_file(file.filename):
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(settings.SUPPORTED_FORMATS)}"
            )

        # Read file content
        content = await file.read()

        # Validate file size
        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE / 1024 / 1024:.0f}MB"
            )

        # Save file
        file_path, file_size = file_manager.save_upload(content, file.filename)

        # Extract metadata
        metadata = file_manager.get_audio_metadata(file_path)

        # Create database record
        audio_file = AudioFile(
            filename=file.filename,
            original_path=file_path,
            file_size=file_size,
            format=file_manager.get_file_format(file.filename),
            **metadata
        )

        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)

        logger.info(f"File uploaded successfully: {file.filename} (ID: {audio_file.id})")

        return audio_file

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Upload failed")


@router.get("/files/{file_id}", response_model=AudioFileResponse)
def get_audio_file(file_id: str, db: Session = Depends(get_db)):
    """
    Get audio file metadata by ID
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()

    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")

    return audio_file


@router.delete("/files/{file_id}", status_code=204)
def delete_audio_file(file_id: str, db: Session = Depends(get_db)):
    """
    Delete an audio file and all associated data
    """
    audio_file = db.query(AudioFile).filter(AudioFile.id == file_id).first()

    if not audio_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Delete file from disk
    file_manager.delete_file(audio_file.original_path)

    # Delete from database (cascade will handle related records)
    db.delete(audio_file)
    db.commit()

    logger.info(f"Deleted audio file: {file_id}")
    return None
