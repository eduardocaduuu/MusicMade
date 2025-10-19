"""Tablature schemas"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class InstrumentType(str, Enum):
    GUITAR = "guitar"
    BASS = "bass"
    PIANO = "piano"


class TablatureCreate(BaseModel):
    instrument_type: InstrumentType
    tuning: str = "standard"


class TablatureResponse(BaseModel):
    id: str
    track_id: str
    instrument_type: str
    tuning: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
