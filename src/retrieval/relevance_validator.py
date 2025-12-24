from typing import List
from .models import RetrievedChunk, ValidationResult
from ..config.logging_config import get_logger


class RelevanceValidator:
    """
    Validates the relevance, ordering, and metadata completeness of retrieval results.
    """

    def __init__(self, min_relevance_threshold: float = 0.5):
        self.min_relevance_threshold = min_relevance_threshold
        self.logger = get_logger(__name__)

    def calculate_relevance_score(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate overall relevance score based on average similarity scores.

        Args:
            chunks: List of retrieved chunks with similarity scores

        Returns:
            Float between 0 and 1 representing overall relevance
        """
        if not chunks:
            return 0.0

        # Calculate average of all similarity scores
        total_score = sum(chunk.score for chunk in chunks)
        avg_score = total_score / len(chunks)

        # Normalize the score to be between 0 and 1
        # Assuming similarity scores are already in the right range from Qdrant
        return min(1.0, max(0.0, avg_score))

    def calculate_ordering_accuracy(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate accuracy of ordering based on similarity scores (descending order).

        Args:
            chunks: List of retrieved chunks that should be ordered by similarity

        Returns:
            Float between 0 and 1 representing ordering accuracy
        """
        if len(chunks) <= 1:
            return 1.0

        # Check how many adjacent pairs are in the correct order (descending by score)
        correct_pairs = 0
        total_pairs = len(chunks) - 1

        for i in range(total_pairs):
            # Current chunk should have >= score of next chunk (descending order)
            if chunks[i].score >= chunks[i + 1].score:
                correct_pairs += 1

        return correct_pairs / total_pairs if total_pairs > 0 else 1.0

    def calculate_metadata_completeness(self, chunks: List[RetrievedChunk]) -> float:
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

    def validate_retrieval_result(self, query_text: str, chunks: List[RetrievedChunk], execution_time: float) -> ValidationResult:
        """
        Perform comprehensive validation of retrieval results.

        Args:
            query_text: The original query text
            chunks: List of retrieved chunks
            execution_time: Time taken for retrieval

        Returns:
            ValidationResult with calculated metrics
        """
        relevance_score = self.calculate_relevance_score(chunks)
        ordering_accuracy = self.calculate_ordering_accuracy(chunks)
        metadata_completeness = self.calculate_metadata_completeness(chunks)
        confidence_threshold_met = relevance_score >= self.min_relevance_threshold

        validation_result = ValidationResult(
            query_text=query_text,
            retrieved_chunks=chunks,
            relevance_score=relevance_score,
            ordering_accuracy=ordering_accuracy,
            metadata_completeness=metadata_completeness,
            execution_time=execution_time,
            confidence_threshold_met=confidence_threshold_met
        )

        # Log validation results
        self.logger.info(
            f"Validation completed - Relevance: {relevance_score:.2f}, "
            f"Ordering: {ordering_accuracy:.2f}, Metadata: {metadata_completeness:.2f}, "
            f"Threshold Met: {confidence_threshold_met}"
        )

        return validation_result