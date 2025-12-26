#!/usr/bin/env python3
"""
Script to run the textbook content ingestion from sitemap using Gemini embeddings.
"""
import asyncio
import sys
import os
import logging
from typing import List, Optional
from uuid import uuid4

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))

from config.settings import settings
from services.sitemap_parser import sitemap_parser
from services.content_extractor import content_extractor, ExtractedContent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Service for generating embeddings using Gemini
    """

    def __init__(self):
        self.gemini_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize the Gemini service"""
        # Initialize Gemini
        try:
            from services.hybrid_embedding import hybrid_embedding_service
            self.gemini_service = hybrid_embedding_service
            logger.info("Hybrid embedding service initialized successfully")
        except Exception as e:
            logger.error(f"Hybrid embedding service initialization failed: {str(e)}")
            raise

        logger.info(f"Using {type(self.gemini_service).__name__} as embedding service")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text using Hybrid service (Gemini with Cohere fallback)"""
        try:
            return await self.gemini_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Hybrid embedding service failed: {str(e)}")
            raise

    async def generate_query_embedding(self, query: str) -> List[float]:
        """Generate query embedding using Hybrid service (Gemini with Cohere fallback)"""
        try:
            return await self.gemini_service.generate_query_embedding(query)
        except Exception as e:
            logger.error(f"Hybrid query embedding service failed: {str(e)}")
            raise

    def validate_embedding(self, embedding: List[float]) -> bool:
        """Validate embedding using the service"""
        return self.gemini_service.validate_embedding(embedding)

class SimpleVectorStoreService:
    """
    Simplified vector store service that connects only when needed
    """
    def __init__(self):
        self.client = None
        self.collection_name = "documentation_pages"
        self._connected = False

    def _ensure_connection(self):
        """
        Lazy initialization of Qdrant connection with proper dimension handling
        """
        if self._connected:
            return

        try:
            from qdrant_client import QdrantClient
            from qdrant_client.http import models

            # Initialize Qdrant client
            self.client = QdrantClient(
                url=settings.qdrant_host,
                api_key=settings.qdrant_api_key,
                prefer_grpc=False  # Using HTTP for simplicity
            )

            # Check if collection exists, create or update if needed
            try:
                collections = self.client.get_collections()
                collection_names = [collection.name for collection in collections.collections]

                if self.collection_name in collection_names:
                    # Check if the collection has the correct dimensions
                    collection_info = self.client.get_collection(self.collection_name)
                    current_dim = collection_info.config.params.vectors.size

                    if current_dim != settings.embedding_dimensions:
                        logger.info(f"Collection exists with wrong dimensions ({current_dim}), deleting and recreating with {settings.embedding_dimensions}")
                        self.client.delete_collection(self.collection_name)
                        collection_exists = False
                    else:
                        logger.info(f"Qdrant collection already exists with correct dimensions: {self.collection_name}")
                        collection_exists = True
                else:
                    collection_exists = False

                if not collection_exists:
                    # Create collection with appropriate vector configuration
                    self.client.create_collection(
                        collection_name=self.collection_name,
                        vectors_config=models.VectorParams(
                            size=settings.embedding_dimensions,  # Updated to match Gemini: 3072
                            distance=models.Distance.COSINE
                        )
                    )

                    # Create payload index for faster filtering
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="url",
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )

                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name="source_hash",
                        field_schema=models.PayloadSchemaType.KEYWORD
                    )

                    logger.info(f"Created Qdrant collection: {self.collection_name} with {settings.embedding_dimensions} dimensions")

            except Exception as e:
                logger.error(f"Error checking/creating collection: {str(e)}")
                raise

            self._connected = True
            logger.info("Successfully connected to Qdrant")

        except Exception as e:
            logger.error(f"Could not connect to Qdrant: {str(e)}")
            logger.info("Continuing without vector store - embeddings will be generated but not stored")
            self.client = None
            self._connected = False

    def store_document(
        self,
        url: str,
        title: str,
        content: str,
        embedding: List[float],
        chunk_id: Optional[str] = None,
        chunk_index: Optional[int] = 0,
        source_hash: Optional[str] = None
    ) -> Optional[str]:
        """
        Store a document chunk with its embedding in Qdrant
        """
        self._ensure_connection()

        if not self.client:
            # If no connection, just return without storing
            logger.warning("No Qdrant connection, skipping storage")
            return None

        try:
            if not chunk_id:
                chunk_id = str(uuid4())

            # Prepare the payload with document metadata
            payload = {
                "url": url,
                "title": title,
                "content": content,
                "chunk_index": chunk_index,
                "created_at": "2025-12-25T10:30:00Z",  # In a real app, use current timestamp
            }

            if source_hash:
                payload["source_hash"] = source_hash

            # Store the point in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[{
                    "id": chunk_id,
                    "vector": embedding,
                    "payload": payload
                }]
            )

            logger.info(f"Stored document chunk: {chunk_id} from {url}")
            return chunk_id

        except Exception as e:
            logger.error(f"Error storing document in Qdrant: {str(e)}")
            return None

# Global instances
embedding_service = EmbeddingService()
vector_store_service = SimpleVectorStoreService()

async def process_single_page(url: str) -> bool:
    """
    Process a single page: extract content, generate embeddings, and store
    """
    try:
        # Extract content from the page
        extracted = content_extractor.extract_content(url)
        if not extracted:
            logger.warning(f"Failed to extract content from {url}")
            return False

        # Chunk the content if it's too large
        chunks = content_extractor.chunk_document(extracted.content)

        # Process each chunk
        for i, chunk in enumerate(chunks):
            chunk_text = chunk["text"]
            chunk_index = chunk["index"]

            # Generate embedding for the chunk
            embedding = await embedding_service.generate_embedding(chunk_text)

            # Store the document chunk in vector store
            chunk_id = str(uuid4())  # Use proper UUID for Qdrant
            stored_id = vector_store_service.store_document(
                url=extracted.url,
                title=extracted.title,
                content=chunk_text,
                embedding=embedding,
                chunk_id=chunk_id,
                chunk_index=chunk_index,
                source_hash=extracted.source_hash
            )

            if stored_id:
                logger.debug(f"Successfully stored chunk {chunk_id}")

        logger.info(f"Successfully processed page: {url} ({len(chunks)} chunks)")
        return True

    except Exception as e:
        logger.error(f"Error processing page {url}: {str(e)}")
        return False

async def ingest_all_urls():
    """
    Main function to ingest ALL pages from a sitemap (no batching)
    """
    logger.info("Starting complete ingestion for ALL URLs...")

    # Get the sitemap URL from settings (loaded from .env)
    sitemap_url = settings.sitemap_url
    logger.info(f"Using sitemap URL: {sitemap_url}")

    # Parse the sitemap to get URLs
    urls = sitemap_parser.parse_sitemap(sitemap_url)
    logger.info(f"Found {len(urls)} total URLs to process")

    if not urls:
        logger.warning(f"No URLs found in sitemap: {sitemap_url}")
        return False

    # Process ALL URLs sequentially to ensure all are processed
    pages_processed = 0
    pages_failed = 0

    for i, url in enumerate(urls):
        logger.info(f"Processing URL {i+1}/{len(urls)}: {url}")

        success = await process_single_page(url)

        if success:
            pages_processed += 1
            logger.debug(f"Successfully processed page {pages_processed}: {url}")
        else:
            pages_failed += 1
            logger.warning(f"Failed to process page: {url}")

        # Log progress every 5 pages or at the end
        if (i + 1) % 5 == 0 or (i + 1) == len(urls):
            logger.info(f"Progress: {i+1}/{len(urls)} - Processed: {pages_processed}, Failed: {pages_failed}")

    # Complete the ingestion summary
    logger.info(f"Complete ingestion finished. Total: {len(urls)}, Processed: {pages_processed}, Failed: {pages_failed}")

    if pages_failed == 0:
        logger.info("All URLs processed successfully!")
    else:
        logger.info(f"Completed with {pages_failed} failures.")

    return True

async def main():
    """
    Main function to run the ingestion process
    """
    logger.info("Starting textbook content ingestion from sitemap using Gemini embeddings...")

    # Get the sitemap URL from settings (loaded from .env)
    sitemap_url = settings.sitemap_url
    logger.info(f"Using sitemap URL: {sitemap_url}")
    logger.info(f"Using embedding model: {settings.embedding_model}")
    logger.info(f"Using embedding dimensions: {settings.embedding_dimensions}")

    # Perform the complete ingestion of all URLs
    logger.info("Starting complete ingestion process...")
    success = await ingest_all_urls()

    if success:
        logger.info("Textbook content ingestion completed successfully!")
        return True
    else:
        logger.error("Textbook content ingestion failed!")
        return False

if __name__ == "__main__":
    logger.info("Textbook content ingestion script starting...")

    try:
        # Run the async main function
        success = asyncio.run(main())
        if success:
            logger.info("Textbook content ingestion completed successfully!")
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)