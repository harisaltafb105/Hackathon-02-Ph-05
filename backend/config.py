"""
Configuration management using Pydantic Settings.
Loads and validates environment variables required for the backend.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Find project root (parent of backend directory)
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings are required and must be provided via environment variables
    or a .env file in the project root.
    """

    # Better Auth Configuration
    better_auth_url: str
    better_auth_secret: str

    # Database Configuration
    database_url: str

    # OpenAI Configuration
    openai_api_key: str

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Global settings instance
# This will fail fast on import if required environment variables are missing
settings = Settings()
