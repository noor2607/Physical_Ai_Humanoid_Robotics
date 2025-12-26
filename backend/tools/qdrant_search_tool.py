import asyncio
from typing import Dict, Any, List, Optional
from config.settings import settings
from services.retrieval_cohere import gemini_retrieval_service
from services.gemini_embedding import gemini_embedding_service
import logging

logger = logging.getLogger(__name__)

class QdrantSearchTool:
    """
    Tool for searching book content ingested in Qdrant vector database
    """

    @staticmethod
    async def search_book_content(query: str, limit: int = 5, url_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search the book content in Qdrant vector database for relevant information

        Args:
            query: Search query to find relevant content
            limit: Maximum number of results to return (default: 5)
            url_filter: Optional URL filter to narrow search scope

        Returns:
            List of relevant documents with metadata
        """
        try:
            logger.info(f"Searching book content for query: '{query[:50]}...'")

            # Use the Gemini retrieval service to search in Qdrant
            retrieved_contexts = await gemini_retrieval_service.search_and_rank(
                query=query,
                limit=limit,
                url_filter=url_filter,
                deduplicate=True
            )

            # Format results for the agent
            results = []
            for ctx in retrieved_contexts:
                results.append({
                    "id": ctx.id,
                    "title": ctx.title,
                    "url": ctx.url,
                    "content": ctx.content[:1000] + "..." if len(ctx.content) > 1000 else ctx.content,  # Truncate long content
                    "relevance_score": round(ctx.relevance_score, 3),
                    "rank": ctx.rank
                })

            logger.info(f"Found {len(results)} relevant documents for query: '{query[:50]}...'")
            return results

        except Exception as e:
            logger.error(f"Error searching book content: {str(e)}")
            return [{"error": f"Search failed: {str(e)}"}]

    @staticmethod
    async def get_content_by_url(url: str) -> List[Dict[str, Any]]:
        """
        Get all content from a specific URL

        Args:
            url: URL to search for content

        Returns:
            List of content from the specified URL
        """
        try:
            logger.info(f"Getting content for URL: {url}")

            retrieved_contexts = await gemini_retrieval_service.retrieve_relevant_documents(
                query="",  # Empty query to get all content for URL
                limit=10,
                url_filter=url
            )

            results = []
            for ctx in retrieved_contexts:
                results.append({
                    "id": ctx.id,
                    "title": ctx.title,
                    "content": ctx.content,
                    "relevance_score": round(ctx.relevance_score, 3)
                })

            logger.info(f"Retrieved {len(results)} documents from URL: {url}")
            return results

        except Exception as e:
            logger.error(f"Error getting content by URL: {str(e)}")
            return [{"error": f"Content retrieval failed: {str(e)}"}]

# Create instance for use
qdrant_search_tool = QdrantSearchTool()