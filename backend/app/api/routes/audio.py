"""
Audio streaming and download endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from app.core.database import get_db
from app.models.track import Track

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/tracks/{track_id}/download")
def download_track(track_id: str, db: Session = Depends(get_db)):
    """
    Download a separated track
    """
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    file_path = Path(track.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Track file not found on disk")

    # Return file for download
    return FileResponse(
        path=str(file_path),
        media_type="audio/wav",
        filename=f"{track.instrument_name}.wav"
    )


@router.get("/tracks/{track_id}/stream")
async def stream_track(track_id: str, db: Session = Depends(get_db)):
    """
    Stream a separated track
    """
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    file_path = Path(track.file_path)

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Track file not found on disk")

    def iterfile():
        with open(file_path, mode="rb") as file_like:
            while chunk := file_like.read(8192):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": f'inline; filename="{track.instrument_name}.wav"'
        }
    )


@router.get("/tracks/{track_id}")
def get_track_info(track_id: str, db: Session = Depends(get_db)):
    """
    Get track information
    """
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    return track.to_dict()
