from qdrant_client import QdrantClient
from qdrant_client.http import models
from typing import List, Dict, Optional, Any
from .models import RetrievedChunk, QdrantSearchResult
from .exceptions import QdrantConnectionError, EmptyResultError
from ..config.settings import settings


class QdrantClientWrapper:
    """
    Wrapper for Qdrant client to handle vector similarity search operations.
    """

    def __init__(self):
        try:
            self.client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                prefer_grpc=False  # Using REST API for better compatibility
            )
            self.collection_name = settings.qdrant_collection_name
        except Exception as e:
            raise QdrantConnectionError(f"Failed to connect to Qdrant: {str(e)}")

    def search(
        self,
        query_vector: List[float],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> QdrantSearchResult:
        """
        Perform vector similarity search in Qdrant.

        Args:
            query_vector: The embedding vector to search for similar items
            top_k: Number of top results to retrieve (defaults to settings.top_k)
            filters: Optional metadata filters to apply during search

        Returns:
            QdrantSearchResult containing the search results
        """
        k = top_k or settings.top_k

        # Build Qdrant filter from provided filters dict
        qdrant_filter = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchText(text=value)
                        )
                    )
                elif isinstance(value, (int, float)):
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )
                elif isinstance(value, list):
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchAny(any=value)
                        )
                    )

            if conditions:
                qdrant_filter = models.Filter(must=conditions)

        try:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=k,
                query_filter=qdrant_filter,
                with_payload=True,  # Include metadata/payload
                with_vectors=True   # Include the vectors in the response
            )

            # Convert Qdrant results to our internal format
            points = []
            for result in search_results:
                point = {
                    "id": result.id,
                    "score": result.score,
                    "payload": result.payload,
                    "vector": result.vector
                }
                points.append(point)

            return QdrantSearchResult(
                points=points,
                query_vector=query_vector,
                search_params={
                    "top_k": k,
                    "filters": filters
                },
                collection_name=self.collection_name
            )

        except Exception as e:
            raise QdrantConnectionError(f"Qdrant search failed: {str(e)}")

    def retrieve_chunks(
        self,
        query_vector: List[float],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve top-K chunks from Qdrant based on similarity to query vector.

        Args:
            query_vector: The embedding vector to search for similar items
            top_k: Number of top results to retrieve (defaults to settings.top_k)
            filters: Optional metadata filters to apply during retrieval

        Returns:
            List of RetrievedChunk objects
        """
        try:
            search_result = self.search(query_vector, top_k, filters)

            if not search_result.points:
                # Instead of raising an error, we could return an empty list
                # based on the requirement to handle empty results gracefully
                return []

            chunks = []
            for point in search_result.points:
                chunk = RetrievedChunk(
                    id=str(point["id"]),
                    content=point["payload"].get("content", ""),
                    score=point["score"],
                    metadata=point["payload"],
                    embedding=point.get("vector")
                )
                chunks.append(chunk)

            return chunks
        except QdrantConnectionError:
            # Re-raise connection errors as they indicate a service issue
            raise
        except Exception as e:
            # For other errors, log and potentially return empty results
            # depending on the specific error handling requirements
            raise e

    def retrieve_chunks_with_fallback(
        self,
        query_vector: List[float],
        top_k: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RetrievedChunk]:
        """
        Retrieve top-K chunks with additional error handling and fallback logic.

        Args:
            query_vector: The embedding vector to search for similar items
            top_k: Number of top results to retrieve (defaults to settings.top_k)
            filters: Optional metadata filters to apply during retrieval

        Returns:
            List of RetrievedChunk objects (empty list if no results or errors)
        """
        try:
            # First, try with the specified filters
            chunks = self.retrieve_chunks(query_vector, top_k, filters)

            # If we get no results and filters were applied, try without filters as a fallback
            if not chunks and filters:
                chunks = self.retrieve_chunks(query_vector, top_k, None)

            return chunks
        except QdrantConnectionError:
            # If there's a connection error, raise it since it's a critical issue
            raise
        except EmptyResultError:
            # Return empty list instead of raising the error, for graceful handling
            return []
        except Exception as e:
            # Log the error and return empty list for graceful degradation
            from ..config.logging_config import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error during chunk retrieval: {str(e)}")
            return []

    def validate_connection(self) -> bool:
        """
        Validate that we can connect to Qdrant and access the collection.

        Returns:
            True if connection is valid, False otherwise
        """
        try:
            # Try to get collection info to verify access
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info is not None
        except Exception:
            return False