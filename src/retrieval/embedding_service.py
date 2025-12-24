import cohere
from typing import List, Optional
from .models import Query
from .exceptions import EmbeddingError, ConfigurationError
from ..config.settings import settings


class CohereEmbeddingService:
    """
    Service for generating embeddings using the Cohere API.
    Uses the same model as Spec 1 to ensure consistency.
    """

    def __init__(self):
        if not settings.cohere_api_key:
            raise ConfigurationError("COHERE_API_KEY environment variable is required")

        self.client = cohere.Client(settings.cohere_api_key)
        self.model_name = settings.cohere_model_name

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate an embedding for the given text using Cohere.

        Args:
            text: The text to embed

        Returns:
            A list of floats representing the embedding vector
        """
        try:
            # Using the embed method from Cohere SDK
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_query"  # Using search_query for queries
            )

            # Extract the embedding from the response
            embeddings = response.embeddings
            if not embeddings or len(embeddings) == 0:
                raise EmbeddingError("No embeddings returned from Cohere API")

            return embeddings[0]  # Return the first (and only) embedding
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embedding: {str(e)}")

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts using Cohere.

        Args:
            texts: List of texts to embed

        Returns:
            A list of embedding vectors (each vector is a list of floats)
        """
        try:
            response = self.client.embed(
                texts=texts,
                model=self.model_name,
                input_type="search_document"  # Using search_document for documents
            )

            embeddings = response.embeddings
            if not embeddings or len(embeddings) != len(texts):
                raise EmbeddingError(f"Expected {len(texts)} embeddings, got {len(embeddings) if embeddings else 0}")

            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings in batch: {str(e)}")

    def process_query_with_embedding(self, query: Query) -> Query:
        """
        Process a query by generating its embedding.

        Args:
            query: The Query object to process

        Returns:
            The Query object with embedding added
        """
        if not query.normalized_text:
            raise EmbeddingError("Query must be normalized before embedding")

        embedding = self.generate_embedding(query.normalized_text)

        # Check if embedding is valid (not all zeros or unusually small values)
        if not embedding or len(embedding) == 0:
            raise EmbeddingError("Generated embedding is empty")

        # Check for low-confidence embeddings (all values close to zero)
        # This is a basic check - in practice, you might have more sophisticated validation
        if all(abs(val) < 1e-6 for val in embedding):
            raise LowConfidenceError("Generated embedding has very low values, indicating low confidence")

        query.embedding = embedding

        return query