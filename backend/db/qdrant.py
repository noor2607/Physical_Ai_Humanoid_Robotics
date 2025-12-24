from qdrant_client import QdrantClient
from qdrant_client.http.models import Filter, SearchRequest, VectorParams, Distance
from core.config import settings
import os

# Check if remote Qdrant settings are available
if settings.QDRANT_URL and settings.QDRANT_API_KEY and settings.QDRANT_COLLECTION:
    # Use remote Qdrant instance
    client = QdrantClient(
        url=settings.QDRANT_URL,
        api_key=settings.QDRANT_API_KEY
    )
    collection_name = settings.QDRANT_COLLECTION
else:
    # Use local persistent Qdrant instance for development
    # Store in a local directory to persist between runs
    local_qdrant_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".qdrant_local")
    client = QdrantClient(path=local_qdrant_path)  # Local persistent storage for development
    collection_name = "local_humanoid_ai_book"

    # Create collection if it doesn't exist
    try:
        client.get_collection(collection_name)
    except:
        # Collection doesn't exist, create it
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=1024, distance=Distance.COSINE)  # Using 1024 for mock embeddings
        )

def search_qdrant(query_vector, limit=5):
    try:
        hits = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True
        ).points
        return [hit.payload["text"] for hit in hits if "text" in hit.payload and hit.payload["text"]]
    except Exception as e:
        print(f"Error searching Qdrant: {e}")
        return []  # Return empty list if search fails
