from fastapi import APIRouter, HTTPException
from models.query import QueryRequest, QueryResponse
from services.query_service import query_service
from services.session_service import session_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=QueryResponse)
async def submit_query(request: QueryRequest):
    """
    Submit a query to the RAG system
    """
    try:
        logger.info(f"Processing query: '{request.query[:50]}...' for session {request.session_id}")

        # Validate the query
        is_valid = await query_service.validate_query(request.query)
        if not is_valid:
            raise HTTPException(status_code=400, detail="Invalid query")

        # Process the query
        response = await query_service.process_query(request)

        # Add query to session history
        if request.session_id:
            session_service.add_query_to_session(request.session_id, response.query_id)

        logger.info(f"Query processed successfully: '{request.query[:50]}...'")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing query '{request.query[:50]}...': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process query: {str(e)}")

@router.get("/health")
async def query_health_check():
    """
    Health check for the query service
    """
    try:
        # Test that required services are available
        from services.retrieval import retrieval_service
        from services.embedding import embedding_service

        # Simple test: generate a quick embedding to verify services
        test_embedding = await embedding_service.generate_embedding("test")
        if not test_embedding:
            raise Exception("Embedding service not responding")

        return {"status": "healthy", "service": "query"}
    except Exception as e:
        logger.error(f"Query service health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Query service unhealthy: {str(e)}")