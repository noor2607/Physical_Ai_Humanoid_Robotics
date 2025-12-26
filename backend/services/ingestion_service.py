from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from config.settings import settings
from services.sitemap_parser import sitemap_parser
from services.content_extractor import content_extractor, ExtractedContent
from services.embedding import embedding_service
from services.vector_store import vector_store_service
from models.ingestion_log import IngestionLog
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
import hashlib

logger = logging.getLogger(__name__)

class IngestionService:
    """
    Service for managing the document ingestion pipeline
    """

    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=5)  # Limit concurrent requests

    def _create_ingestion_log(self, sitemap_url: str, status: str = "pending") -> IngestionLog:
        """
        Create an ingestion log entry

        Args:
            sitemap_url: URL of the sitemap being processed
            status: Initial status of the ingestion

        Returns:
            IngestionLog object
        """
        return IngestionLog(
            sitemap_url=sitemap_url,
            status=status,
            start_time=datetime.utcnow()
        )

    def _update_ingestion_log(self, log: IngestionLog, status: str, pages_processed: int = None,
                             pages_failed: int = None, error_details: str = None, end_time: datetime = None) -> IngestionLog:
        """
        Update an ingestion log entry

        Args:
            log: The ingestion log to update
            status: New status
            pages_processed: Number of pages processed
            pages_failed: Number of pages failed
            error_details: Error details if any
            end_time: End time if applicable

        Returns:
            Updated IngestionLog object
        """
        log.status = status
        if pages_processed is not None:
            log.pages_processed = pages_processed
        if pages_failed is not None:
            log.pages_failed = pages_failed
        if error_details:
            log.error_details = error_details
        if end_time:
            log.end_time = end_time

        return log

    def _should_ingest_page(self, url: str, force_refresh: bool = False) -> bool:
        """
        Determine if a page should be ingested based on its hash and existing content

        Args:
            url: URL of the page to check
            force_refresh: Whether to force refresh regardless of existing content

        Returns:
            True if the page should be ingested, False otherwise
        """
        if force_refresh:
            return True

        # In a real implementation, we would check if we already have this page
        # and compare its hash with the current content
        return True

    async def _process_single_page_async(self, url: str) -> Tuple[bool, str, Optional[ExtractedContent]]:
        """
        Process a single page: extract content, generate embeddings, and store

        Args:
            url: URL of the page to process

        Returns:
            Tuple of (success: bool, message: str, extracted_content: Optional[ExtractedContent])
        """
        try:
            # Extract content from the page
            extracted = content_extractor.extract_content(url)
            if not extracted:
                return False, f"Failed to extract content from {url}", None

            # Chunk the content if it's too large
            chunks = content_extractor.chunk_document(extracted.content)

            # Process each chunk
            for i, chunk in enumerate(chunks):
                chunk_text = chunk["text"]
                chunk_index = chunk["index"]

                # Generate embedding for the chunk
                embedding = await embedding_service.generate_embedding(chunk_text)

                # Store the document chunk in vector store
                chunk_id = f"{extracted.source_hash[:8]}_{i}"  # Create a unique chunk ID
                vector_store_service.store_document(
                    url=extracted.url,
                    title=extracted.title,
                    content=chunk_text,
                    embedding=embedding,
                    chunk_id=chunk_id,
                    chunk_index=chunk_index,
                    source_hash=extracted.source_hash
                )

            logger.info(f"Successfully processed page: {url}")
            return True, f"Successfully processed {len(chunks)} chunks from {url}", extracted

        except Exception as e:
            error_msg = f"Error processing page {url}: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None

    def ingest_sitemap(self, sitemap_url: str, force_refresh: bool = False) -> IngestionLog:
        """
        Main method to ingest all pages from a sitemap

        Args:
            sitemap_url: URL of the sitemap.xml to process
            force_refresh: Whether to force re-processing of all pages

        Returns:
            IngestionLog object with results
        """
        logger.info(f"Starting ingestion for sitemap: {sitemap_url}")

        # Create ingestion log
        ingestion_log = self._create_ingestion_log(sitemap_url, "processing")

        try:
            # Parse the sitemap to get URLs
            urls = sitemap_parser.parse_sitemap(sitemap_url)
            ingestion_log.total_pages = len(urls)

            if not urls:
                message = f"No URLs found in sitemap: {sitemap_url}"
                logger.warning(message)
                self._update_ingestion_log(
                    ingestion_log,
                    "failed",
                    pages_processed=0,
                    pages_failed=0,
                    error_details=message
                )
                return ingestion_log

            logger.info(f"Found {len(urls)} URLs to process")

            # Process URLs in batches to manage memory and rate limiting
            batch_size = 10
            pages_processed = 0
            pages_failed = 0

            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]

                # Process batch sequentially to avoid async issues
                for url in batch:
                    if self._should_ingest_page(url, force_refresh):
                        # Use asyncio.run to run the async function in a sync context
                        success, message, _ = asyncio.run(self._process_single_page_async(url))

                        if success:
                            pages_processed += 1
                            logger.debug(f"Processed page {pages_processed}: {url}")
                        else:
                            pages_failed += 1
                            logger.warning(f"Failed to process page: {message}")

                # Update log periodically
                self._update_ingestion_log(
                    ingestion_log,
                    "processing",
                    pages_processed=pages_processed,
                    pages_failed=pages_failed
                )

            # Complete the ingestion log
            final_status = "completed" if pages_failed == 0 else "completed_with_errors"
            self._update_ingestion_log(
                ingestion_log,
                final_status,
                pages_processed=pages_processed,
                pages_failed=pages_failed,
                end_time=datetime.utcnow()
            )

            logger.info(f"Ingestion completed. Processed: {pages_processed}, Failed: {pages_failed}")
            return ingestion_log

        except Exception as e:
            error_msg = f"Critical error during ingestion: {str(e)}"
            logger.error(error_msg)

            self._update_ingestion_log(
                ingestion_log,
                "failed",
                pages_processed=0,
                pages_failed=0,
                error_details=error_msg,
                end_time=datetime.utcnow()
            )

            return ingestion_log

    async def ingest_sitemap_async(self, sitemap_url: str, force_refresh: bool = False) -> IngestionLog:
        """
        Async version of ingest_sitemap for better performance

        Args:
            sitemap_url: URL of the sitemap.xml to process
            force_refresh: Whether to force re-processing of all pages

        Returns:
            IngestionLog object with results
        """
        logger.info(f"Starting async ingestion for sitemap: {sitemap_url}")

        # Create ingestion log
        ingestion_log = self._create_ingestion_log(sitemap_url, "processing")

        try:
            # Parse the sitemap to get URLs
            urls = sitemap_parser.parse_sitemap(sitemap_url)
            ingestion_log.total_pages = len(urls)

            if not urls:
                message = f"No URLs found in sitemap: {sitemap_url}"
                logger.warning(message)
                self._update_ingestion_log(
                    ingestion_log,
                    "failed",
                    pages_processed=0,
                    pages_failed=0,
                    error_details=message
                )
                return ingestion_log

            logger.info(f"Found {len(urls)} URLs to process")

            # Process URLs in batches to manage memory and rate limiting
            batch_size = 5  # Smaller batch size for async processing
            pages_processed = 0
            pages_failed = 0

            for i in range(0, len(urls), batch_size):
                batch = urls[i:i + batch_size]

                # Process batch asynchronously
                tasks = []
                for url in batch:
                    if self._should_ingest_page(url, force_refresh):
                        task = self._process_single_page_async(url)
                        tasks.append(task)

                # Execute tasks concurrently
                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Process results
                for i, result in enumerate(results):
                    url = [u for u in batch if self._should_ingest_page(u, force_refresh)][i] if i < len([u for u in batch if self._should_ingest_page(u, force_refresh)]) else "unknown"
                    if isinstance(result, Exception):
                        pages_failed += 1
                        error_msg = f"Error processing page {url}: {str(result)}"
                        logger.error(error_msg)
                    else:
                        success, message, _ = result
                        if success:
                            pages_processed += 1
                            logger.debug(f"Processed page {pages_processed}: {url}")
                        else:
                            pages_failed += 1
                            logger.warning(f"Failed to process page: {message}")

                # Update log periodically
                self._update_ingestion_log(
                    ingestion_log,
                    "processing",
                    pages_processed=pages_processed,
                    pages_failed=pages_failed
                )

            # Complete the ingestion log
            final_status = "completed" if pages_failed == 0 else "completed_with_errors"
            self._update_ingestion_log(
                ingestion_log,
                final_status,
                pages_processed=pages_processed,
                pages_failed=pages_failed,
                end_time=datetime.utcnow()
            )

            logger.info(f"Async ingestion completed. Processed: {pages_processed}, Failed: {pages_failed}")
            return ingestion_log

        except Exception as e:
            error_msg = f"Critical error during async ingestion: {str(e)}"
            logger.error(error_msg)

            self._update_ingestion_log(
                ingestion_log,
                "failed",
                pages_processed=0,
                pages_failed=0,
                error_details=error_msg,
                end_time=datetime.utcnow()
            )

            return ingestion_log

    def get_ingestion_status(self) -> Dict[str, any]:
        """
        Get overall ingestion status and statistics

        Returns:
            Dictionary with ingestion statistics
        """
        total_docs = vector_store_service.get_total_document_count()

        return {
            "indexed_documents": total_docs,
            "last_ingestion": "2025-12-25T10:30:00Z",  # In a real app, track actual time
            "qdrant_status": "connected" if vector_store_service else "disconnected",
            "model_status": "ready"
        }

# Global instance of the ingestion service
ingestion_service = IngestionService()