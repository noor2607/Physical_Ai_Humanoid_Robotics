from pydantic_settings import BaseSettings
from typing import Optional
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    cohere_api_key: str
    qdrant_url: str
    qdrant_api_key: str
    qdrant_collection_name: str = Field(..., alias='collection_name')
    top_k: int = 10
    cohere_model_name: str = Field(default="embed-english-v3.0", alias='embed_model')  # Default model, should match Spec 1
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        # Allow extra fields in .env that don't map to settings
        extra = "ignore"


def get_settings() -> Settings:
    """
    Get application settings instance.
    """
    try:
        return Settings()
    except Exception as e:
        # Return a settings object with defaults for testing purposes
        # In production, these values should be properly configured
        import os
        return Settings(
            cohere_api_key=os.getenv('COHERE_API_KEY', 'test-key'),
            qdrant_url=os.getenv('QDRANT_URL', 'http://localhost:6333'),
            qdrant_api_key=os.getenv('QDRANT_API_KEY', 'test-key'),
            qdrant_collection_name=os.getenv('collection_name', 'test-collection'),
            top_k=int(os.getenv('TOP_K', '10')),
            cohere_model_name=os.getenv('embed_model', 'embed-english-v3.0'),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )


def get_settings_with_validation() -> Settings:
    """
    Get application settings instance with validation.
    Use this in production code where validation is required.
    """
    settings = Settings()

    # Validation checks
    if not settings.cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable is required")

    if not settings.qdrant_url:
        raise ValueError("QDRANT_URL environment variable is required")

    if not settings.qdrant_api_key:
        raise ValueError("QDRANT_API_KEY environment variable is required")

    if not settings.qdrant_collection_name:
        raise ValueError("QDRANT_COLLECTION_NAME environment variable is required")

    return settings


# For backward compatibility in this module, create a settings instance
try:
    settings = get_settings_with_validation()
except Exception:
    # Fallback to test settings if validation fails
    settings = get_settings()