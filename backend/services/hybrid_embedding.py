import google.generativeai as genai
import cohere
from typing import List
from config.settings import settings
import logging
import time
import asyncio
from functools import wraps
from services.gemini_embedding import GeminiEmbeddingService
from services.cohere_embedding import CohereEmbeddingService

logger = logging.getLogger(__name__)

class HybridEmbeddingService:
    """
    Service for generating embeddings using Gemini as primary and Cohere as fallback
    when Gemini hits API quota limits.
    """

    def __init__(self):
        # Initialize both embedding services
        self.gemini_service = GeminiEmbeddingService()
        self.cohere_service = CohereEmbeddingService()

        # Use the higher dimension (3072 from Gemini) as the standard
        # Cohere will be adjusted to match this if needed
        self.embedding_dimensions = 3072

        logger.info("Initialized Hybrid Embedding Service with Gemini (primary) and Cohere (fallback)")

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using Gemini first, falling back to Cohere if needed

        Args:
            text: Input text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """
        # Try Gemini first
        try:
            embedding = await self.gemini_service.generate_embedding(text)
            # Validate the embedding dimensions
            if len(embedding) == self.embedding_dimensions:
                return embedding
            else:
                logger.warning(f"Gemini returned embedding with {len(embedding)} dimensions, expected {self.embedding_dimensions}")
                # If dimensions don't match, try Cohere
        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a quota limit error
            if "quota" in error_msg or "429" in error_msg or "limit" in error_msg:
                logger.warning(f"Gemini quota exceeded, falling back to Cohere: {str(e)}")
            else:
                logger.warning(f"Gemini failed, falling back to Cohere: {str(e)}")

        # Fall back to Cohere
        try:
            embedding = await self.cohere_service.generate_embedding(text)
            # If Cohere returns 1024 dimensions but we need 3072, we need to handle this
            if len(embedding) != self.embedding_dimensions:
                logger.warning(f"Cohere returned embedding with {len(embedding)} dimensions, expected {self.embedding_dimensions}")
                # For now, we'll pad or truncate to match expected dimensions
                # In a real scenario, we'd want to ensure both services return the same dimensions
                if len(embedding) < self.embedding_dimensions:
                    # Pad with zeros
                    embedding.extend([0.0] * (self.embedding_dimensions - len(embedding)))
                else:
                    # Truncate
                    embedding = embedding[:self.embedding_dimensions]
            return embedding
        except Exception as e:
            logger.error(f"Both Gemini and Cohere failed to generate embedding: {str(e)}")
            raise

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a batch of texts, using fallback mechanism

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
                # Return a zero vector in case of error
                embeddings.append([0.0] * self.embedding_dimensions)

        return embeddings

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a query, using fallback mechanism

        Args:
            query: User query text

        Returns:
            List of floats representing the query embedding vector
        """
        # Try Gemini first for query embedding
        try:
            embedding = await self.gemini_service.generate_query_embedding(query)
            # Validate the embedding dimensions
            if len(embedding) == self.embedding_dimensions:
                return embedding
            else:
                logger.warning(f"Gemini query embedding returned {len(embedding)} dimensions, expected {self.embedding_dimensions}")
        except Exception as e:
            error_msg = str(e).lower()
            # Check if it's a quota limit error
            if "quota" in error_msg or "429" in error_msg or "limit" in error_msg:
                logger.warning(f"Gemini quota exceeded for query, falling back to Cohere: {str(e)}")
            else:
                logger.warning(f"Gemini failed for query, falling back to Cohere: {str(e)}")

        # Fall back to Cohere for query embedding
        try:
            embedding = await self.cohere_service.generate_query_embedding(query)
            # Adjust dimensions if needed
            if len(embedding) != self.embedding_dimensions:
                logger.warning(f"Cohere query embedding returned {len(embedding)} dimensions, expected {self.embedding_dimensions}")
                if len(embedding) < self.embedding_dimensions:
                    # Pad with zeros
                    embedding.extend([0.0] * (self.embedding_dimensions - len(embedding)))
                else:
                    # Truncate
                    embedding = embedding[:self.embedding_dimensions]
            return embedding
        except Exception as e:
            logger.error(f"Both Gemini and Cohere failed to generate query embedding: {str(e)}")
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

        if len(embedding) != self.embedding_dimensions:
            logger.warning(f"Embedding has {len(embedding)} dimensions, expected {self.embedding_dimensions}")
            return False

        # Check if all values are numbers
        for value in embedding:
            if not isinstance(value, (int, float)):
                logger.warning("Embedding contains non-numeric values")
                return False

        return True

    async def get_embedding_dimensions(self) -> int:
        """
        Get the expected dimensions for embeddings

        Returns:
            Number of dimensions in the embedding vectors
        """
        return self.embedding_dimensions

# Global instance of the hybrid embedding service
hybrid_embedding_service = HybridEmbeddingService()