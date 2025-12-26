from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import uuid4

class IngestionLog(BaseModel):
    """
    Tracks the ingestion process for monitoring and debugging
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the log entry (UUID)")
    sitemap_url: str = Field(..., description="URL of the sitemap being processed")
    status: str = Field(..., description="Status of the ingestion (pending, processing, completed, failed)")
    pages_processed: int = Field(default=0, ge=0, description="Number of pages successfully processed")
    pages_failed: int = Field(default=0, ge=0, description="Number of pages that failed to process")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="When the ingestion started")
    end_time: Optional[datetime] = Field(default=None, description="When the ingestion completed")
    error_details: Optional[str] = Field(default=None, description="Details of any errors that occurred")
    total_pages: int = Field(default=0, ge=0, description="Total number of pages discovered in the sitemap")

    @validator('status')
    def validate_status(cls, v):
        """Validate that status is one of the allowed values"""
        allowed_statuses = ['pending', 'processing', 'completed', 'failed']
        if v.lower() not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v.lower()

    @validator('pages_processed', 'pages_failed', 'total_pages')
    def validate_non_negative(cls, v):
        """Validate that page counts are non-negative integers"""
        if v < 0:
            raise ValueError('Page counts must be non-negative integers')
        return v

    @validator('end_time')
    def validate_time_order(cls, v, values):
        """Validate that start time is before end time (for completed tasks)"""
        if v is not None:
            start_time = values.get('start_time')
            if start_time and v < start_time:
                raise ValueError('End time must be after start time')
        return v

    @validator('sitemap_url')
    def validate_sitemap_url(cls, v):
        """Validate that sitemap URL is a valid HTTP/HTTPS URL"""
        import re
        if not re.match(r'^https?://', v):
            raise ValueError('Sitemap URL must be a valid HTTP/HTTPS URL')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class IngestionRequest(BaseModel):
    """
    Request model for triggering ingestion
    """
    sitemap_url: str = Field(
        default="https://physical-ai-humanoid-robotics-tan-ten.vercel.app/sitemap.xml",
        description="URL of the sitemap.xml to process"
    )
    force_refresh: bool = Field(
        default=False,
        description="Whether to force re-processing of all pages even if unchanged"
    )

    @validator('sitemap_url')
    def validate_sitemap_url(cls, v):
        """Validate that sitemap URL is a valid HTTP/HTTPS URL"""
        import re
        if not re.match(r'^https?://', v):
            raise ValueError('Sitemap URL must be a valid HTTP/HTTPS URL')
        return v

class IngestionResponse(BaseModel):
    """
    Response model for ingestion results
    """
    status: str
    job_id: str
    pages_processed: int
    pages_failed: int
    total_pages: int
    processing_time: str
    message: Optional[str] = None