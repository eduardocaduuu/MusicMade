"""
File management service for handling uploads and storage
"""
import os
import shutil
from pathlib import Path
from typing import Optional
import uuid
import librosa
import soundfile as sf

from app.core.config import settings


class FileManager:
    """Manage file operations for audio files"""

    def __init__(self):
        self.upload_path = Path(settings.UPLOAD_PATH)
        self.temp_path = Path(settings.TEMP_PATH)
        self.models_path = Path(settings.MODELS_PATH)

        # Ensure directories exist
        self.upload_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
        self.models_path.mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_content: bytes, filename: str) -> tuple[str, int]:
        """
        Save uploaded file and return (file_path, file_size)
        """
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = Path(filename).suffix
        unique_filename = f"{file_id}{file_extension}"
        file_path = self.upload_path / unique_filename

        # Save file
        with open(file_path, "wb") as f:
            f.write(file_content)

        file_size = len(file_content)
        return str(file_path), file_size

    def get_audio_metadata(self, file_path: str) -> dict:
        """
        Extract audio metadata using librosa
        Returns: dict with duration, sample_rate, channels
        """
        try:
            # Load audio file
            y, sr = librosa.load(file_path, sr=None, mono=False)

            # Determine channels
            if y.ndim == 1:
                channels = 1
            else:
                channels = y.shape[0]

            # Calculate duration
            duration = librosa.get_duration(y=y, sr=sr)

            return {
                "duration": float(duration),
                "sample_rate": int(sr),
                "channels": int(channels)
            }
        except Exception as e:
            print(f"Error extracting metadata: {e}")
            return {
                "duration": None,
                "sample_rate": None,
                "channels": None
            }

    def validate_audio_file(self, filename: str) -> bool:
        """
        Validate if file is a supported audio format
        """
        extension = Path(filename).suffix.lower().lstrip('.')
        return extension in settings.SUPPORTED_FORMATS

    def get_file_format(self, filename: str) -> Optional[str]:
        """Get file format from filename"""
        return Path(filename).suffix.lower().lstrip('.')

    def delete_file(self, file_path: str) -> bool:
        """
        Delete a file safely
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def delete_directory(self, dir_path: str) -> bool:
        """
        Delete a directory and all its contents
        """
        try:
            path = Path(dir_path)
            if path.exists() and path.is_dir():
                shutil.rmtree(path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting directory: {e}")
            return False

    def create_job_directory(self, job_id: str) -> Path:
        """
        Create a directory for a separation job
        """
        job_dir = self.temp_path / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        return job_dir

    def get_track_path(self, job_id: str, instrument_name: str) -> str:
        """
        Get the expected path for a separated track
        """
        job_dir = self.temp_path / job_id
        return str(job_dir / f"{instrument_name}.wav")


# Global instance
file_manager = FileManager()
