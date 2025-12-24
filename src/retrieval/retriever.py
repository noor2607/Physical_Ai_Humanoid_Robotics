import time
from typing import List, Dict, Optional, Any
from .models import Query, RetrievedChunk, ValidationResult
from .query_processor import QueryProcessor
from .embedding_service import CohereEmbeddingService
from .qdrant_client import QdrantClientWrapper
from ..config.settings import settings
from ..config.logging_config import get_logger


class Retriever:
    """
    Orchestrator that connects query processing, embedding generation, and Qdrant search.
    """

    def __init__(self):
        self.query_processor = QueryProcessor()
        self.embedding_service = CohereEmbeddingService()
        self.qdrant_client = QdrantClientWrapper()
        self.logger = get_logger(__name__)

    def retrieve(
        self,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> ValidationResult:
        """
        Retrieve relevant chunks for a given query text.

        Args:
            query_text: The raw query text
            filters: Optional metadata filters to apply
            top_k: Number of top results to retrieve (defaults to settings.top_k)

        Returns:
            ValidationResult containing the retrieved chunks and metadata
        """
        start_time = time.time()

        try:
            # Step 1: Validate and process the query with enhanced validation
            validated_query_text, validated_filters = self.query_processor.validate_and_filter_query(query_text, filters)
            query = self.query_processor.process_query(validated_query_text, validated_filters)
            self.query_processor.validate_query(query)

            # Step 2: Generate embedding for the normalized query
            query = self.embedding_service.process_query_with_embedding(query)

            # Step 3: Search in Qdrant with fallback logic for graceful error handling
            retrieved_chunks = self.qdrant_client.retrieve_chunks_with_fallback(
                query_vector=query.embedding,
                top_k=top_k,
                filters=validated_filters
            )

            # Step 4: Calculate execution time
            execution_time = time.time() - start_time

            # Step 5: Create validation result
            # Calculate metadata completeness based on available chunks
            metadata_completeness = self._calculate_metadata_completeness(retrieved_chunks) if retrieved_chunks else 0.0

            # For now, we'll set placeholder values for relevance and ordering
            # These will be properly calculated when using the full validation pipeline
            validation_result = ValidationResult(
                query_text=query_text,
                retrieved_chunks=retrieved_chunks,
                relevance_score=0.0,  # Will be calculated in full validation
                ordering_accuracy=0.0,  # Will be calculated in full validation
                metadata_completeness=metadata_completeness,
                execution_time=execution_time,
                confidence_threshold_met=len(retrieved_chunks) > 0  # Basic check: did we get results?
            )

            # Log retrieval status
            if retrieved_chunks:
                self.logger.info(
                    f"Retrieved {len(retrieved_chunks)} chunks for query in {execution_time:.2f}s"
                )
            else:
                self.logger.info(
                    f"No chunks retrieved for query in {execution_time:.2f}s"
                )

            # Verify performance constraint
            if execution_time > 2.0:  # 2 seconds constraint from spec
                self.logger.warning(
                    f"Retrieval took {execution_time:.2f}s, exceeding 2s performance goal"
                )

            return validation_result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Retrieval failed after {execution_time:.2f}s: {str(e)}")
            # Don't raise the exception in some cases - return a validation result with error info
            error_result = ValidationResult(
                query_text=query_text,
                retrieved_chunks=[],
                relevance_score=0.0,
                ordering_accuracy=0.0,
                metadata_completeness=0.0,
                execution_time=execution_time,
                confidence_threshold_met=False
            )
            # Re-raise for now to maintain original behavior
            raise e

    def _calculate_metadata_completeness(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate the percentage of chunks with complete metadata.

        Args:
            chunks: List of RetrievedChunk objects

        Returns:
            Float between 0 and 1 representing metadata completeness
        """
        if not chunks:
            return 0.0

        required_fields = ["url", "title", "chunk_index"]
        complete_chunks = 0

        for chunk in chunks:
            has_all_required = all(field in chunk.metadata for field in required_fields)
            if has_all_required:
                complete_chunks += 1

        return complete_chunks / len(chunks)

    def validate_query_and_retrieve(
        self,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate the query and retrieve results (convenience method).

        Args:
            query_text: The raw query text
            filters: Optional metadata filters to apply
            top_k: Number of top results to retrieve (defaults to settings.top_k)

        Returns:
            ValidationResult containing the retrieved chunks and metadata
        """
        # This method is essentially the same as retrieve for now
        # Additional validation could be added here in the future
        return self.retrieve(query_text, filters, top_k)