from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import API routers
from api.v1.router import api_router

# Import middleware
from middleware.error_handler import setup_exception_handlers

# Import services for chat endpoint compatibility
from models.query import QueryRequest
from services.query_service import query_service

# Create FastAPI app instance
app = FastAPI(
    title="AI Textbook RAG Chatbot API",
    description="API for the RAG-based AI chatbot system that ingests documentation and provides intelligent answers",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup exception handlers
app = setup_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "AI Textbook RAG Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-12-25T10:30:00Z"}

@app.post("/chat")
async def chat_endpoint(request: dict):
    """
    Compatibility endpoint for frontend chat service
    Uses the new Gemini agent service with Qdrant content search
    """
    from fastapi import HTTPException
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Extract query from frontend request format
        query_text = request.get("question", "")
        context = request.get("selected_text", "")  # Context from selected text
        session_id = request.get("sessionId", "default_session")

        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")

        logger.info(f"Processing chat query through Gemini agent: '{query_text[:50]}...' from session {session_id}")

        # Import and use the new Gemini agent service
        from services.gemini_agent_service import gemini_agent_service

        # Process the query through the agent service
        result = await gemini_agent_service.run_query(query_text)

        # Transform the result to match frontend expectations
        response = {
            "answer": result["answer"],
            "sources": [source["url"] for source in result["sources"]],  # Extract URLs as sources
            "confidence": result["confidence"],
            "success": True
        }

        logger.info(f"Chat query processed successfully by Gemini agent: '{query_text[:50]}...'")
        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they are
        raise
    except Exception as e:
        logger.error(f"Error processing chat query '{request.get('question', '')[:50]}...': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process chat query: {str(e)}")


@app.get("/agent/capabilities")
async def agent_capabilities():
    """
    Get the capabilities of the Gemini agent service
    """
    from services.gemini_agent_service import gemini_agent_service
    return await gemini_agent_service.get_agent_capabilities()


@app.post("/agent/query")
async def agent_query_endpoint(request: dict):
    """
    Direct endpoint for agent queries with full response details
    """
    from fastapi import HTTPException
    import logging

    logger = logging.getLogger(__name__)

    try:
        query_text = request.get("query", "")
        if not query_text:
            raise HTTPException(status_code=400, detail="Query is required")

        logger.info(f"Processing direct agent query: '{query_text[:50]}...'")

        from services.gemini_agent_service import gemini_agent_service
        result = await gemini_agent_service.run_query(query_text)

        logger.info(f"Direct agent query processed successfully: '{query_text[:50]}...'")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing direct agent query '{request.get('query', '')[:50]}...': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process agent query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )