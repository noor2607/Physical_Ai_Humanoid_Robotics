"""
Custom exceptions for the Qdrant retrieval validation system.
"""


class RetrievalError(Exception):
    """
    Base exception for retrieval-related errors.
    """
    pass


class EmbeddingError(RetrievalError):
    """
    Exception raised when there are issues with embedding generation.
    """
    pass


class QdrantConnectionError(RetrievalError):
    """
    Exception raised when there are connection issues with Qdrant.
    """
    pass


class QueryValidationError(RetrievalError):
    """
    Exception raised when query validation fails.
    """
    pass


class EmptyResultError(RetrievalError):
    """
    Exception raised when the retrieval returns no results.
    """
    pass


class ConfigurationError(RetrievalError):
    """
    Exception raised when there are configuration issues.
    """
    pass


class LowConfidenceError(RetrievalError):
    """
    Exception raised when the confidence score is below the threshold.
    """
    pass