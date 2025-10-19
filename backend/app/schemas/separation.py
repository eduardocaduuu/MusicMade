"""Separation job schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class Algorithm(str, Enum):
    DEMUCS = "demucs"
    SPLEETER = "spleeter"


class Quality(str, Enum):
    FAST = "fast"
    HIGH = "high"


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class SeparationJobCreate(BaseModel):
    algorithm: Algorithm = Algorithm.DEMUCS
    quality: Quality = Quality.FAST


class JobStatusUpdate(BaseModel):
    status: JobStatus
    progress: float = Field(ge=0, le=100)
    error_message: Optional[str] = None


class SeparationJobResponse(BaseModel):
    id: str
    audio_file_id: str
    status: JobStatus
    algorithm: str
    quality: str
    progress: float
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    tracks: List["TrackResponse"] = []

    class Config:
        from_attributes = True


# Import to resolve forward reference
from .track import TrackResponse
SeparationJobResponse.model_rebuild()
