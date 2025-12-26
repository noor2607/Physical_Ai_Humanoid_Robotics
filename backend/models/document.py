from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID, uuid4
import re

class Document(BaseModel):
    """
    Represents a single documentation page from the sitemap
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique identifier for the document (UUID)")
    url: str = Field(..., description="Source URL of the documentation page")
    title: str = Field(..., description="Title of the documentation page (extracted from HTML)")
    content: str = Field(..., description="Extracted and cleaned text content")
    chunk_id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="Identifier for this chunk of the document (for large documents)")
    chunk_text: str = Field(..., description="The specific chunk of text stored")
    chunk_index: int = Field(default=0, description="Sequential index of this chunk within the document")
    embedding: Optional[List[float]] = Field(default=None, description="Vector embedding of the chunk text")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the document was indexed")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when the document was last updated")
    source_hash: Optional[str] = Field(default=None, description="Hash of the original content to detect changes")

    @validator('url')
    def validate_url(cls, v):
        """Validate that URL is a valid HTTP/HTTPS URL"""
        if not re.match(r'^https?://', v):
            raise ValueError('URL must be a valid HTTP/HTTPS URL')
        return v

    @validator('content')
    def validate_content_length(cls, v):
        """Validate that content does not exceed maximum embedding model input length"""
        from config.settings import settings
        if len(v) > settings.max_content_length:
            raise ValueError(f'Content must not exceed {settings.max_content_length} characters')
        if not v.strip():
            raise ValueError('Content must not be empty')
        return v

    @validator('embedding')
    def validate_embedding(cls, v):
        """Validate that embedding vector has exactly 768 dimensions"""
        if v is not None:
            from config.settings import settings
            if len(v) != settings.embedding_dimensions:
                raise ValueError(f'Embedding vector must have exactly {settings.embedding_dimensions} dimensions')
        return v

    @validator('title')
    def validate_title(cls, v):
        """Validate that title is not empty"""
        if not v.strip():
            raise ValueError('Title must not be empty')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class DocumentChunk(BaseModel):
    """
    Represents a chunk of a document for processing and storage
    """
    document_id: str
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    chunk_text: str
    chunk_index: int = 0
    embedding: Optional[List[float]] = None
    url: str
    title: str

    @validator('chunk_text')
    def validate_chunk_text(cls, v):
        """Validate that chunk text is not empty"""
        if not v.strip():
            raise ValueError('Chunk text must not be empty')
        return v

class DocumentIngestionRequest(BaseModel):
    """
    Request model for triggering document ingestion
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
        if not re.match(r'^https?://', v):
            raise ValueError('Sitemap URL must be a valid HTTP/HTTPS URL')
        return v