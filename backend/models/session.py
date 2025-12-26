from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import uuid4

class Session(BaseModel):
    """
    Represents a user session with conversation history
    """
    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique session identifier (UUID)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="When the session was started")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="When the session was last used")
    query_history: List[str] = Field(default_factory=list, description="List of query IDs in this session")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional session metadata (user info, etc.)")
    expires_at: Optional[datetime] = Field(default=None, description="When the session expires")

    @validator('id')
    def validate_session_id(cls, v):
        """Validate that session ID is not empty"""
        if not v.strip():
            raise ValueError('Session ID must not be empty')
        return v

    @validator('query_history')
    def validate_query_history(cls, v):
        """Validate that query history items are valid"""
        # In a real implementation, we would validate that these IDs reference valid queries
        return v

    @validator('expires_at')
    def validate_expires_at(cls, v, values):
        """Validate that session has an expiration time"""
        if v is None:
            # Set default expiration time (e.g., 24 hours from creation)
            from config.settings import settings
            import timedelta
            from datetime import timedelta
            v = values.get('created_at', datetime.utcnow()) + timedelta(hours=24)
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SessionRequest(BaseModel):
    """
    Request model for session-related operations
    """
    session_id: Optional[str] = Field(default_factory=lambda: str(uuid4()), description="Session identifier")

    @validator('session_id')
    def validate_session_id(cls, v):
        """Validate that session ID is not empty"""
        if v and not v.strip():
            raise ValueError('Session ID must not be empty')
        return v

class SessionResponse(BaseModel):
    """
    Response model for session details
    """
    session_id: str
    created_at: str
    last_activity: str
    query_count: int
    queries: List[dict]