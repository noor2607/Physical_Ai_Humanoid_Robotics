import os
from typing import Optional


class Settings:
    def __init__(self):
        self.backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
        self.qdrant_url: str = os.getenv("QDRANT_URL", "")
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.neon_db_url: str = os.getenv("NEON_DB_URL", "")


settings = Settings()