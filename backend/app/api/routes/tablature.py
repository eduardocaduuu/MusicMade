"""
Tablature generation endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.models.track import Track
from app.models.tablature import Tablature
from app.schemas.tablature import TablatureCreate, TablatureResponse
from app.services.tablature_generator import tablature_generator

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/tracks/{track_id}/tablature", response_model=TablatureResponse, status_code=201)
async def generate_tablature(
    track_id: str,
    params: TablatureCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate tablature from a separated track
    """
    # Get track
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        # Generate tablature
        logger.info(f"Generating {params.instrument_type} tablature for track {track_id}")

        tab_content = tablature_generator.generate_tablature(
            audio_path=track.file_path,
            instrument_type=params.instrument_type.value,
            tuning=params.tuning
        )

        # Save to database
        tablature = Tablature(
            track_id=track_id,
            instrument_type=params.instrument_type.value,
            tuning=params.tuning,
            content=tab_content
        )

        db.add(tablature)
        db.commit()
        db.refresh(tablature)

        logger.info(f"Generated tablature {tablature.id} for track {track_id}")

        return tablature

    except Exception as e:
        logger.error(f"Tablature generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tablature generation failed: {str(e)}")


@router.get("/tablature/{tablature_id}", response_model=TablatureResponse)
def get_tablature(tablature_id: str, db: Session = Depends(get_db)):
    """
    Get tablature by ID
    """
    tablature = db.query(Tablature).filter(Tablature.id == tablature_id).first()

    if not tablature:
        raise HTTPException(status_code=404, detail="Tablature not found")

    return tablature


@router.get("/tracks/{track_id}/tablatures", response_model=List[TablatureResponse])
def list_track_tablatures(track_id: str, db: Session = Depends(get_db)):
    """
    List all tablatures for a track
    """
    track = db.query(Track).filter(Track.id == track_id).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    tablatures = db.query(Tablature).filter(Tablature.track_id == track_id).all()
    return tablatures


@router.delete("/tablature/{tablature_id}", status_code=204)
def delete_tablature(tablature_id: str, db: Session = Depends(get_db)):
    """
    Delete a tablature
    """
    tablature = db.query(Tablature).filter(Tablature.id == tablature_id).first()

    if not tablature:
        raise HTTPException(status_code=404, detail="Tablature not found")

    db.delete(tablature)
    db.commit()

    logger.info(f"Deleted tablature: {tablature_id}")
    return None
