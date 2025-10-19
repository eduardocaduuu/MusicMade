"""Track schemas"""
from pydantic import BaseModel
from typing import Optional


class TrackBase(BaseModel):
    instrument_name: str
    duration: Optional[float] = None
    file_size: Optional[int] = None


class TrackResponse(TrackBase):
    id: str
    separation_job_id: str

    class Config:
        from_attributes = True
