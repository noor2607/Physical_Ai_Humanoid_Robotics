from typing import List, Dict, Optional, Any
from .models import Query, RetrievedChunk, ValidationResult
from .relevance_validator import RelevanceValidator
from .qdrant_client import QdrantClientWrapper
from .embedding_service import CohereEmbeddingService
from .query_processor import QueryProcessor
from ..config.settings import settings
from ..config.logging_config import get_logger


class RetrievalValidator:
    """
    Main validator class that orchestrates the entire retrieval validation process.
    """

    def __init__(self, min_relevance_threshold: float = 0.5):
        self.relevance_validator = RelevanceValidator(min_relevance_threshold)
        self.qdrant_client = QdrantClientWrapper()
        self.embedding_service = CohereEmbeddingService()
        self.query_processor = QueryProcessor()
        self.logger = get_logger(__name__)

    def validate_query(
        self,
        query_text: str,
        filters: Optional[Dict[str, Any]] = None,
        top_k: Optional[int] = None
    ) -> ValidationResult:
        """
        Validate a query by retrieving results and evaluating their quality.

        Args:
            query_text: The raw query text to validate
            filters: Optional metadata filters to apply
            top_k: Number of top results to retrieve (defaults to settings.top_k)

        Returns:
            ValidationResult containing the quality metrics
        """
        import time
        start_time = time.time()

        try:
            # Process the query
            query = self.query_processor.process_query(query_text, filters)
            self.query_processor.validate_query(query)

            # Generate embedding
            query = self.embedding_service.process_query_with_embedding(query)

            # Retrieve chunks from Qdrant
            retrieved_chunks = self.qdrant_client.retrieve_chunks(
                query_vector=query.embedding,
                top_k=top_k,
                filters=filters
            )

            # Calculate execution time
            execution_time = time.time() - start_time

            # Validate the retrieval results
            validation_result = self.relevance_validator.validate_retrieval_result(
                query_text=query_text,
                chunks=retrieved_chunks,
                execution_time=execution_time
            )

            return validation_result

        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(f"Validation failed after {execution_time:.2f}s: {str(e)}")
            raise e

    def validate_relevance(self, query_text: str, expected_chunks: List[RetrievedChunk]) -> float:
        """
        Validate relevance against expected results.

        Args:
            query_text: The query text
            expected_chunks: List of chunks that should be considered relevant

        Returns:
            Float representing the relevance accuracy against expected results
        """
        # This would typically compare retrieved results against known good results
        # For now, we'll just return the standard relevance score calculation
        # In a real implementation, you'd have a way to compare against ground truth
        result = self.validate_query(query_text)
        return result.relevance_score