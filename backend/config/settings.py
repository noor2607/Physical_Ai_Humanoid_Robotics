from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    openai_api_key: str = os.getenv("OPENROUTER_API_KEY", "")  # Using OpenRouter API key from .env
    cohere_api_key: Optional[str] = os.getenv("COHERE_API_KEY", "")
    neon_database_url: Optional[str] = os.getenv("NEON_DATABASE_URL", "")

    # Qdrant Configuration
    qdrant_host: str = os.getenv("QDRANT_URL", "localhost")  # Using QDRANT_URL from .env
    qdrant_port: int = int(os.getenv("QDRANT_PORT", 6333))
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")

    # Application Settings
    sitemap_url: str = os.getenv("SITEMAP_URL", "https://physical-ai-humanoid-robotics-tan-ten.vercel.app/sitemap.xml")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "info")

    # Server Configuration
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    workers: int = int(os.getenv("WORKERS", 1))  # Add workers setting

    # Embedding Configuration
    embedding_model: str = "gemini-embedding-001"  # Gemini embedding model
    embedding_dimensions: int = 3072  # Dimension for Gemini embeddings (3072 for gemini-embedding-001)

    # Document Processing
    max_content_length: int = 10000  # Maximum length of content to process
    chunk_size: int = 1000  # Size of document chunks
    chunk_overlap: int = 200  # Overlap between document chunks

    # API Configuration
    max_query_length: int = 1000  # Maximum length of user queries
    max_results: int = 5  # Maximum number of results to return

    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields in .env that aren't defined in the model

# Create a global settings instance
settings = Settings()