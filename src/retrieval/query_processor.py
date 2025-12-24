import re
from typing import Dict, Optional
from .models import Query
from .exceptions import QueryValidationError


class QueryProcessor:
    """
    Handles query normalization and preprocessing before embedding generation.
    """

    def __init__(self):
        self.logger = None  # Will be set by the main application

    def normalize_query(self, query_text: str) -> str:
        """
        Normalize the query text by applying standard preprocessing steps.

        Args:
            query_text: The raw query text to normalize

        Returns:
            The normalized query text
        """
        if not query_text or not query_text.strip():
            raise QueryValidationError("Query text cannot be empty or whitespace only")

        # Check for extremely long queries
        if len(query_text) > 1000:  # Arbitrary limit, can be configured
            raise QueryValidationError("Query text is too long (>1000 characters)")

        # Convert to lowercase
        normalized = query_text.lower()

        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        # Remove special characters but keep essential punctuation
        # Keep letters, numbers, spaces, and common punctuation
        normalized = re.sub(r'[^\w\s\-\.\,\!\?\;\:]', ' ', normalized)

        # Remove extra whitespace again after character removal
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def validate_and_filter_query(self, query_text: str, filters: Optional[Dict] = None) -> tuple[str, Optional[Dict]]:
        """
        Validate the query and apply any necessary filtering.

        Args:
            query_text: The raw query text
            filters: Optional metadata filters

        Returns:
            Tuple of (validated_query_text, validated_filters)
        """
        # Validate query text
        if not query_text or not query_text.strip():
            raise QueryValidationError("Query text cannot be empty")

        # Check for extremely long queries
        if len(query_text) > 10000:  # More generous limit for validation
            raise QueryValidationError("Query text exceeds maximum allowed length")

        # Validate filters if provided
        if filters is not None:
            if not isinstance(filters, dict):
                raise QueryValidationError("Filters must be a dictionary")

            # Validate filter values
            for key, value in filters.items():
                if not isinstance(key, str):
                    raise QueryValidationError(f"Filter key '{key}' must be a string")
                if value is None:
                    raise QueryValidationError(f"Filter value for key '{key}' cannot be None")

        return query_text, filters

    def process_query(self, query_text: str, filters: Optional[Dict] = None) -> Query:
        """
        Process a raw query into a normalized Query object.

        Args:
            query_text: The raw query text
            filters: Optional metadata filters to apply

        Returns:
            A Query object with normalized text
        """
        normalized_text = self.normalize_query(query_text)

        return Query(
            text=query_text,
            normalized_text=normalized_text,
            filters=filters or {}
        )

    def validate_query(self, query: Query) -> bool:
        """
        Validate a query object.

        Args:
            query: The Query object to validate

        Returns:
            True if the query is valid, False otherwise
        """
        if not query.text or not query.text.strip():
            raise QueryValidationError("Query text cannot be empty")

        if query.filters and not isinstance(query.filters, dict):
            raise QueryValidationError("Filters must be a dictionary")

        # Additional validation can be added here

        return True