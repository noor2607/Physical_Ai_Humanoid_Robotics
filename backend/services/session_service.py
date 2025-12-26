from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from config.settings import settings
from models.session import Session, SessionRequest, SessionResponse
import uuid

logger = logging.getLogger(__name__)

class SessionService:
    """
    Service for managing user sessions and conversation history
    """

    def __init__(self):
        # In-memory storage for sessions (in production, use a database)
        self.sessions: Dict[str, Session] = {}
        self.session_timeout = timedelta(hours=24)  # Session expires after 24 hours

    def create_session(self) -> Session:
        """
        Create a new user session

        Returns:
            Session object
        """
        session_id = str(uuid.uuid4())
        session = Session(
            id=session_id,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            expires_at=datetime.utcnow() + self.session_timeout
        )

        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by its ID

        Args:
            session_id: ID of the session to retrieve

        Returns:
            Session object if found, None otherwise
        """
        if session_id in self.sessions:
            session = self.sessions[session_id]

            # Check if session has expired
            if session.expires_at and datetime.utcnow() > session.expires_at:
                self.delete_session(session_id)
                return None

            # Update last activity time
            session.last_activity = datetime.utcnow()
            return session

        return None

    def update_session(self, session: Session) -> Session:
        """
        Update an existing session

        Args:
            session: Session object to update

        Returns:
            Updated Session object
        """
        if session.id in self.sessions:
            session.last_activity = datetime.utcnow()
            self.sessions[session.id] = session
            return session

        raise ValueError(f"Session {session.id} does not exist")

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session

        Args:
            session_id: ID of the session to delete

        Returns:
            True if session was deleted, False if it didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def add_query_to_session(self, session_id: str, query_id: str) -> bool:
        """
        Add a query ID to a session's history

        Args:
            session_id: ID of the session
            query_id: ID of the query to add

        Returns:
            True if query was added, False if session doesn't exist
        """
        session = self.get_session(session_id)
        if session:
            if query_id not in session.query_history:
                session.query_history.append(query_id)
                session.last_activity = datetime.utcnow()
                self.sessions[session_id] = session
                logger.debug(f"Added query {query_id} to session {session_id}")
                return True
        return False

    def get_session_history(self, session_id: str) -> List[str]:
        """
        Get the query history for a session

        Args:
            session_id: ID of the session

        Returns:
            List of query IDs in the session
        """
        session = self.get_session(session_id)
        if session:
            return session.query_history
        return []

    def cleanup_expired_sessions(self) -> int:
        """
        Remove expired sessions from memory

        Returns:
            Number of sessions cleaned up
        """
        current_time = datetime.utcnow()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if session.expires_at and current_time > session.expires_at
        ]

        for session_id in expired_sessions:
            del self.sessions[session_id]
            logger.info(f"Cleaned up expired session: {session_id}")

        return len(expired_sessions)

    def get_session_response(self, session_id: str) -> Optional[SessionResponse]:
        """
        Get session details formatted as a response

        Args:
            session_id: ID of the session to get details for

        Returns:
            SessionResponse object if session exists, None otherwise
        """
        session = self.get_session(session_id)
        if session:
            # For now, return basic session info
            # In a real implementation, we would fetch query details
            return SessionResponse(
                session_id=session.id,
                created_at=session.created_at.isoformat(),
                last_activity=session.last_activity.isoformat(),
                query_count=len(session.query_history),
                queries=[]  # Would fetch actual query details in a real implementation
            )
        return None

    def extend_session(self, session_id: str, extension_hours: int = 24) -> bool:
        """
        Extend a session's expiration time

        Args:
            session_id: ID of the session to extend
            extension_hours: Number of hours to extend the session

        Returns:
            True if session was extended, False if session doesn't exist
        """
        session = self.get_session(session_id)
        if session:
            session.expires_at = datetime.utcnow() + timedelta(hours=extension_hours)
            session.last_activity = datetime.utcnow()
            self.sessions[session_id] = session
            logger.info(f"Extended session {session_id} by {extension_hours} hours")
            return True
        return False

# Global instance of the session service
session_service = SessionService()