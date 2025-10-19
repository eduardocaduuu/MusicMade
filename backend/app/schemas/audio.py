"""Audio file schemas"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AudioFileBase(BaseModel):
    filename: str
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    file_size: int
    format: Optional[str] = None


class AudioFileCreate(AudioFileBase):
    original_path: str


class AudioFileResponse(AudioFileBase):
    id: str
    upload_date: datetime

    class Config:
        from_attributes = True
