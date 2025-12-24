import google.generativeai as genai
import os
import sys

# Add the project root to Python path if needed
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from core.config import settings
from db.qdrant import search_qdrant
import logging
from typing import List

# Only configure Google API if the key is available
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)

EMBED_MODEL = "models/embedding-001"

def embed_text(text: str):
    """
    Generate embeddings using Cohere API if available, otherwise fall back to mock embeddings
    """
    import os
    from core.config import settings

    # Check if COHERE_API_KEY is available in settings
    cohere_api_key = os.getenv("COHERE_API_KEY") or getattr(settings, 'COHERE_API_KEY', None)

    if cohere_api_key:
        # Use Cohere API for real embeddings
        try:
            import cohere
            co = cohere.Client(cohere_api_key)

            # Generate embedding using Cohere
            response = co.embed(
                texts=[text],
                model="embed-english-v3.0",  # Latest English embedding model
                input_type="search_query"  # Specify this is for search
            )

            return response.embeddings[0]  # Return the embedding vector

        except Exception as e:
            print(f"Cohere embedding failed: {str(e)}, falling back to mock embedding")
            # Fall back to mock embedding if Cohere fails

    # Fallback to mock embedding if Cohere is not available or fails
    vector_size = 1024  # Standard size for compatibility
    import hashlib
    import math

    # Initialize vector with small random-like values based on text
    vector = []
    for i in range(vector_size):
        combined = f"{text[:100]}_{i}_salt".encode('utf-8')
        hash_val = int(hashlib.md5(combined).hexdigest(), 16)
        # Normalize to [-1, 1] range
        value = ((hash_val % 2000) / 1000.0) - 1.0
        vector.append(value)

    # Add influence from character n-grams to create similarity for related text
    text_lower = text.lower()
    for i in range(len(text_lower) - 2):
        ngram = text_lower[i:i+3]
        hash_val = int(hashlib.md5(ngram.encode()).hexdigest(), 16)
        pos = hash_val % vector_size
        # Add the ngram influence to the existing value
        vector[pos] += ((hash_val * 7) % 1000) / 2000.0 - 0.25  # Smaller adjustment

    # Add influence from word patterns (for better semantic meaning)
    words = text_lower.split()
    for j, word in enumerate(words):
        if len(word) > 2:  # Only consider meaningful words
            word_hash = int(hashlib.md5(word.encode()).hexdigest(), 16)
            pos = (word_hash * j + len(word)) % vector_size  # Include position in text
            vector[pos] += ((word_hash * 11) % 1000) / 2000.0 - 0.25  # Smaller adjustment

    # Normalize the vector to unit length to match typical embedding behavior
    magnitude = math.sqrt(sum(x**2 for x in vector))
    if magnitude > 0:
        vector = [x / magnitude for x in vector]

    # Ensure the vector has exactly the right size
    return vector[:vector_size]

def retrieve_context(question: str):
    vector = embed_text(question)
    return search_qdrant(vector)
