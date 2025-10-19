"""
Application configuration using Pydantic Settings
"""
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, validator
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "MusicMade API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production")
    ALLOWED_ORIGINS: str = Field(default="*")

    # Database
    DATABASE_URL: str = Field(default="sqlite:///./music_separator.db")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")

    # File Storage
    MAX_FILE_SIZE: int = Field(default=104857600)  # 100MB
    UPLOAD_PATH: str = Field(default="./uploads")
    MODELS_PATH: str = Field(default="./models")
    TEMP_PATH: str = Field(default="./temp")

    # Audio Processing
    DEFAULT_SEPARATOR: str = Field(default="demucs")  # demucs or spleeter
    SUPPORTED_FORMATS: List[str] = ["mp3", "wav", "flac", "mp4", "m4a"]

    # Celery
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    # Render specific
    RENDER_EXTERNAL_URL: Optional[str] = None
    PORT: int = Field(default=8000)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    @validator("CELERY_BROKER_URL", pre=True, always=True)
    def set_celery_broker(cls, v, values):
        """Set Celery broker URL from Redis URL if not provided"""
        if v:
            return v
        return values.get("REDIS_URL", "redis://localhost:6379")

    @validator("CELERY_RESULT_BACKEND", pre=True, always=True)
    def set_celery_backend(cls, v, values):
        """Set Celery result backend from Redis URL if not provided"""
        if v:
            return v
        return values.get("REDIS_URL", "redis://localhost:6379")

    @validator("ALLOWED_ORIGINS")
    def parse_origins(cls, v):
        """Parse comma-separated origins"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    def get_origins_list(self) -> List[str]:
        """Get CORS allowed origins as list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            if self.ALLOWED_ORIGINS == "*":
                return ["*"]
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
        return self.ALLOWED_ORIGINS

    def create_directories(self):
        """Create necessary directories if they don't exist"""
        for path in [self.UPLOAD_PATH, self.MODELS_PATH, self.TEMP_PATH]:
            os.makedirs(path, exist_ok=True)


# Create global settings instance
settings = Settings()

# Create directories on startup
settings.create_directories()
