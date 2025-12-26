import cohere
from typing import List, Union
from config.settings import settings
import logging
import time
import asyncio
from functools import wraps

logger = logging.getLogger(__name__)

class CohereEmbeddingService:
    """
    Service for generating embeddings using Cohere API
    """

    def __init__(self):
        # Initialize the Cohere API with the API key
        self.client = cohere.Client(settings.cohere_api_key)

        # Get the embedding model name
        self.model_name = settings.embedding_model

        # Rate limiting configuration
        self.requests_per_minute = 60  # Adjust based on your API plan
        self.min_request_interval = 60.0 / self.requests_per_minute
        self.last_request_time = 0.0

    def _rate_limit(func):
        """
        Decorator to implement rate limiting for API calls
        """
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            current_time = time.time()
            time_since_last_request = current_time - self.last_request_time

            if time_since_last_request < self.min_request_interval:
                sleep_time = self.min_request_interval - time_since_last_request
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

            self.last_request_time = time.time()
            return await func(self, *args, **kwargs)

        return wrapper

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Cohere

        Args:
            text: Input text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """
        try:
            # Ensure text is within length limits
            if len(text) > settings.max_content_length:
                text = text[:settings.max_content_length]
                logger.warning(f"Text truncated to {settings.max_content_length} characters for embedding generation")

            # Generate embedding using Cohere API
            response = self.client.embed(
                texts=[text],
                model=self.model_name,
                input_type="search_document"  # Using search_document for knowledge base
            )

            # Extract the embedding from the response
            embedding = response.embeddings[0]  # Get the first (and only) embedding

            logger.debug(f"Generated embedding of length {len(embedding)} for text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding for text: {str(e)}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts using Cohere

        Args:
            texts: List of input texts to generate embeddings for

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        embeddings = []

        for text in texts:
            try:
                embedding = await self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.error(f"Error generating embedding for text '{text[:50]}...': {str(e)}")
                # Return a zero vector in case of error, or raise exception based on requirements
                embeddings.append([0.0] * settings.embedding_dimensions)

        return embeddings

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query specifically for retrieval tasks using Cohere

        Args:
            query: User query text

        Returns:
            List of floats representing the query embedding vector
        """
        try:
            # Validate query length
            if len(query) > settings.max_query_length:
                query = query[:settings.max_query_length]
                logger.warning(f"Query truncated to {settings.max_query_length} characters")

            # For queries, use input_type="search_query" to optimize for retrieval
            response = self.client.embed(
                texts=[query],
                model=self.model_name,
                input_type="search_query"
            )

            # Extract the embedding from the response
            embedding = response.embeddings[0]

            logger.debug(f"Generated query embedding of length {len(embedding)} for query of length {len(query)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating query embedding: {str(e)}")
            raise

    def validate_embedding(self, embedding: List[float]) -> bool:
        """
        Validate that an embedding has the correct dimensions

        Args:
            embedding: Embedding vector to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(embedding, list):
            return False

        if len(embedding) != settings.embedding_dimensions:
            logger.warning(f"Embedding has {len(embedding)} dimensions, expected {settings.embedding_dimensions}")
            return False

        # Check if all values are numbers
        for value in embedding:
            if not isinstance(value, (int, float)):
                logger.warning("Embedding contains non-numeric values")
                return False

        return True

    async def get_embedding_dimensions(self) -> int:
        """
        Get the expected dimensions for embeddings from this model

        Returns:
            Number of dimensions in the embedding vectors
        """
        return settings.embedding_dimensions

# Global instance of the embedding service
cohere_embedding_service = CohereEmbeddingService()