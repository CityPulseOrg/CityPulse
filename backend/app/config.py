"""
CityPulse Configuration
Loads environment variables and provides app settings.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str 

    # Backboard AI Integration
    backboard_api_key: str = "" 
    backboard_workflow_id: str = ""
    backboard_api_url: str = "https://api.backboard.ai"

    # Application
    app_name: str = "CityPulse"
    debug: bool = False

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

