from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
from models.ingestion_log import IngestionRequest, IngestionResponse
from services.ingestion_service import ingestion_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/", response_model=IngestionResponse)
async def trigger_ingestion(request: IngestionRequest):
    """
    Trigger documentation ingestion from sitemap
    """
    try:
        logger.info(f"Starting ingestion for sitemap: {request.sitemap_url}")

        # Perform the ingestion
        ingestion_log = ingestion_service.ingest_sitemap(
            sitemap_url=request.sitemap_url,
            force_refresh=request.force_refresh
        )

        # Calculate processing time
        if ingestion_log.start_time and ingestion_log.end_time:
            processing_time_delta = ingestion_log.end_time - ingestion_log.start_time
            processing_time = f"{processing_time_delta.total_seconds():.1f} seconds"
        else:
            processing_time = "unknown"

        response = IngestionResponse(
            status=ingestion_log.status,
            job_id=ingestion_log.id,
            pages_processed=ingestion_log.pages_processed,
            pages_failed=ingestion_log.pages_failed,
            total_pages=ingestion_log.total_pages,
            processing_time=processing_time,
            message=f"Ingestion completed. Processed: {ingestion_log.pages_processed}, Failed: {ingestion_log.pages_failed}"
        )

        logger.info(f"Ingestion completed for {request.sitemap_url}. Processed: {ingestion_log.pages_processed}, Failed: {ingestion_log.pages_failed}")
        return response

    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process sitemap: {str(e)}")

@router.get("/status")
async def get_ingestion_status():
    """
    Get the current status of the ingestion system
    """
    try:
        status = ingestion_service.get_ingestion_status()
        return status
    except Exception as e:
        logger.error(f"Error getting ingestion status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ingestion status: {str(e)}")