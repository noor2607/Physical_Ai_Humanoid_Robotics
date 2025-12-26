from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import uuid4

class RetrievedContext(BaseModel):
    """
    Represents relevant document chunks retrieved for a query
    """
    query_id: str = Field(..., description="Reference to the original query")
    document_id: str = Field(..., description="Reference to the relevant document chunk")
    content_snippet: str = Field(..., description="Relevant text snippet from the document")
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score (0.0 to 1.0)")
    rank: int = Field(..., ge=1, description="Rank of relevance in the result set")
    source_url: str = Field(..., description="Original URL of the documentation page")
    source_title: str = Field(..., description="Title of the source documentation page")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the context was retrieved")

    @validator('similarity_score')
    def validate_similarity_score(cls, v):
        """Validate that similarity score is between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Similarity score must be between 0.0 and 1.0')
        return v

    @validator('rank')
    def validate_rank(cls, v):
        """Validate that rank is a positive integer"""
        if v < 1:
            raise ValueError('Rank must be a positive integer')
        return v

    @validator('content_snippet')
    def validate_content_snippet(cls, v):
        """Validate that content snippet is not empty"""
        if not v.strip():
            raise ValueError('Content snippet must not be empty')
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RetrievedContextResponse(BaseModel):
    """
    Response model for retrieved context
    """
    id: str
    content: str
    url: str
    title: str
    relevance_score: float
    rank: int

    @validator('relevance_score')
    def validate_relevance_score(cls, v):
        """Validate that relevance score is between 0.0 and 1.0"""
        if not 0.0 <= v <= 1.0:
            raise ValueError('Relevance score must be between 0.0 and 1.0')
        return v

    @validator('rank')
    def validate_rank(cls, v):
        """Validate that rank is a positive integer"""
        if v < 1:
            raise ValueError('Rank must be a positive integer')
        return v