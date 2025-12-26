from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional, Any
from uuid import uuid4
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service for interacting with Qdrant vector database to store and retrieve document embeddings
    """

    def __init__(self):
        # Initialize Qdrant client
        self.client = QdrantClient(
            url=settings.qdrant_host,
            api_key=settings.qdrant_api_key,
            prefer_grpc=False  # Using HTTP for simplicity
        )

        # Collection name for storing documentation
        self.collection_name = "documentation_pages"

        # Initialize the collection if it doesn't exist (but handle connection issues gracefully)
        try:
            self._initialize_collection()
        except Exception as e:
            logger.warning(f"Could not initialize Qdrant collection during startup: {str(e)}")
            logger.info("Qdrant will be initialized on first use")
            self._collection_initialized = False
        else:
            self._collection_initialized = True

    def _ensure_collection_initialized(self):
        """
        Ensure the Qdrant collection is initialized, creating it if necessary
        """
        if hasattr(self, '_collection_initialized') and self._collection_initialized:
            return  # Already initialized

        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [collection.name for collection in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection with appropriate vector configuration
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=models.VectorParams(
                        size=settings.embedding_dimensions,  # 3072 for Gemini embeddings
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

                logger.info(f"Created Qdrant collection: {self.collection_name}")
            else:
                logger.info(f"Qdrant collection already exists: {self.collection_name}")

            self._collection_initialized = True

        except Exception as e:
            logger.error(f"Error initializing Qdrant collection: {str(e)}")
            raise

    def _initialize_collection(self):
        """
        Initialize the Qdrant collection with proper schema for storing document embeddings
        """
        self._ensure_collection_initialized()

    def store_document(
        self,
        url: str,
        title: str,
        content: str,
        embedding: List[float],
        chunk_id: Optional[str] = None,
        chunk_index: Optional[int] = 0,
        source_hash: Optional[str] = None
    ) -> str:
        """
        Store a document chunk with its embedding in Qdrant

        Args:
            url: Source URL of the documentation page
            title: Title of the documentation page
            content: Content of the document chunk
            embedding: Vector embedding of the content
            chunk_id: Optional unique identifier for this chunk
            chunk_index: Sequential index of this chunk within the document
            source_hash: Hash of the original content to detect changes

        Returns:
            str: ID of the stored point in Qdrant
        """
        try:
            self._ensure_collection_initialized()

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
                points=[
                    models.PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload=payload
                    )
                ]
            )

            logger.info(f"Stored document chunk: {chunk_id} from {url}")
            return chunk_id

        except Exception as e:
            logger.error(f"Error storing document in Qdrant: {str(e)}")
            raise

    def batch_store_documents(
        self,
        documents: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store multiple document chunks in batch for efficiency

        Args:
            documents: List of document dictionaries with url, title, content, embedding, etc.

        Returns:
            List[str]: IDs of the stored points in Qdrant
        """
        try:
            self._ensure_collection_initialized()

            points = []
            ids = []

            for doc in documents:
                chunk_id = doc.get('chunk_id', str(uuid4()))
                ids.append(chunk_id)

                payload = {
                    "url": doc["url"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "chunk_index": doc.get("chunk_index", 0),
                    "created_at": "2025-12-25T10:30:00Z",  # In a real app, use current timestamp
                }

                if doc.get("source_hash"):
                    payload["source_hash"] = doc["source_hash"]

                points.append(
                    models.PointStruct(
                        id=chunk_id,
                        vector=doc["embedding"],
                        payload=payload
                    )
                )

            # Batch store points in Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )

            logger.info(f"Batch stored {len(documents)} document chunks")
            return ids

        except Exception as e:
            logger.error(f"Error batch storing documents in Qdrant: {str(e)}")
            raise

    def search_documents(
        self,
        query_embedding: List[float],
        limit: int = 5,
        url_filter: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant documents based on query embedding

        Args:
            query_embedding: Vector embedding of the user query
            limit: Maximum number of results to return
            url_filter: Optional filter to search within specific URL

        Returns:
            List of dictionaries containing document content and metadata
        """
        try:
            self._ensure_collection_initialized()

            # Prepare search filter if needed
            search_filter = None
            if url_filter:
                search_filter = models.Filter(
                    must=[
                        models.FieldCondition(
                            key="url",
                            match=models.MatchValue(value=url_filter)
                        )
                    ]
                )

            # Perform search in Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                query_filter=search_filter,
                limit=limit
            )

            # Format results
            results = []
            for hit in search_results:
                result = {
                    "id": hit.id,
                    "content": hit.payload.get("content", ""),
                    "url": hit.payload.get("url", ""),
                    "title": hit.payload.get("title", ""),
                    "similarity_score": hit.score,
                    "chunk_index": hit.payload.get("chunk_index", 0)
                }
                results.append(result)

            logger.info(f"Found {len(results)} relevant documents for query")
            return results

        except Exception as e:
            logger.error(f"Error searching documents in Qdrant: {str(e)}")
            raise

    def get_document_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific document by its ID

        Args:
            doc_id: ID of the document to retrieve

        Returns:
            Dictionary containing document content and metadata, or None if not found
        """
        try:
            self._ensure_collection_initialized()

            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[doc_id]
            )

            if points:
                point = points[0]
                return {
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "url": point.payload.get("url", ""),
                    "title": point.payload.get("title", ""),
                    "chunk_index": point.payload.get("chunk_index", 0)
                }

            return None

        except Exception as e:
            logger.error(f"Error retrieving document by ID: {str(e)}")
            raise

    def delete_documents_by_url(self, url: str) -> int:
        """
        Delete all document chunks associated with a specific URL

        Args:
            url: URL of documents to delete

        Returns:
            Number of documents deleted
        """
        try:
            self._ensure_collection_initialized()

            # Find all points with the given URL
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="url",
                            match=models.MatchValue(value=url)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected number of chunks per document
            )

            ids_to_delete = [hit.id for hit in search_results[0]]

            if ids_to_delete:
                # Delete the points
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.PointIdsList(
                        points=ids_to_delete
                    )
                )

                logger.info(f"Deleted {len(ids_to_delete)} document chunks for URL: {url}")
                return len(ids_to_delete)

            return 0

        except Exception as e:
            logger.error(f"Error deleting documents by URL: {str(e)}")
            raise

    def get_total_document_count(self) -> int:
        """
        Get the total number of document chunks stored in the collection

        Returns:
            Total number of document chunks
        """
        try:
            self._ensure_collection_initialized()
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except Exception as e:
            logger.error(f"Error getting document count: {str(e)}")
            return 0

# Global instance of the vector store service
vector_store_service = VectorStoreService()