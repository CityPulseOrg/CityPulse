"""
CityPulse Configuration
Loads environment variables and provides app settings.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str

    # Backboard AI Integration
    backboard_api_key: str = ""
    backboard_api_url: str = "https://api.backboard.ai"
    assistant_id: str = ""

    # Application
    app_name: str = "CityPulse"
    debug: bool = False

    # CORS Configuration
    cors_origins: str = ""

    @field_validator('backboard_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        if not v or v == "your_api_key_here":
            raise ValueError(
                "BACKBOARD_API_KEY is required. Get one from https://backboard.ai"
            )
        return v

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
