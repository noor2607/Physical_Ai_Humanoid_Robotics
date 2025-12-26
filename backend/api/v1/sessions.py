from fastapi import APIRouter, HTTPException
from models.session import SessionRequest, SessionResponse
from services.session_service import session_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session_details(session_id: str):
    """
    Get session details including query history
    """
    try:
        logger.info(f"Getting session details for: {session_id}")

        session_response = session_service.get_session_response(session_id)
        if not session_response:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Retrieved session details for: {session_id}")
        return session_response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error getting session details for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session details: {str(e)}")

@router.post("/create")
async def create_new_session():
    """
    Create a new session
    """
    try:
        session = session_service.create_session()
        logger.info(f"Created new session: {session.id}")
        return {"session_id": session.id, "created_at": session.created_at.isoformat()}

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session
    """
    try:
        success = session_service.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Deleted session: {session_id}")
        return {"message": f"Session {session_id} deleted successfully"}

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete session: {str(e)}")

@router.get("/{session_id}/history")
async def get_session_history(session_id: str):
    """
    Get the query history for a session
    """
    try:
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        history = session_service.get_session_history(session_id)
        logger.info(f"Retrieved history for session {session_id}: {len(history)} queries")
        return {"session_id": session_id, "query_count": len(history), "query_ids": history}

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error getting session history for {session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session history: {str(e)}")