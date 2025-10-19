"""
API dependencies
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db


def get_current_db() -> Session:
    """Get database session"""
    return Depends(get_db)
