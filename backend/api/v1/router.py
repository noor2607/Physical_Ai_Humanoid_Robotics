from fastapi import APIRouter
from . import ingestion, query, sessions

# Create API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(ingestion.router, prefix="/ingest", tags=["ingestion"])
api_router.include_router(query.router, prefix="/query", tags=["query"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])

# Add health check endpoint
@api_router.get("/status", tags=["status"])
async def get_status():
    from services.ingestion_service import ingestion_service
    return ingestion_service.get_ingestion_status()