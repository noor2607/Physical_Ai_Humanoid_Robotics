import asyncio
from typing import Dict, Any, List
from config.settings import settings
from services.retrieval import retrieval_service
from services.query_service import query_service
from services.embedding import embedding_service
from models.query import QueryRequest
import logging

logger = logging.getLogger(__name__)

class RAGTools:
    """
    Collection of tools for the RAG system that can be used by the OpenAI Agent
    """

    @staticmethod
    async def search_documentation(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the documentation database for relevant content

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            retrieved_contexts = await retrieval_service.search_and_rank(
                query=query,
                limit=limit
            )

            results = []
            for ctx in retrieved_contexts:
                results.append({
                    "id": ctx.id,
                    "title": ctx.title,
                    "url": ctx.url,
                    "content": ctx.content[:500] + "..." if len(ctx.content) > 500 else ctx.content,  # Truncate long content
                    "relevance_score": ctx.relevance_score
                })

            logger.info(f"Documentation search completed for query: '{query[:50]}...'. Found {len(results)} results.")
            return results

        except Exception as e:
            logger.error(f"Error in documentation search: {str(e)}")
            return [{"error": f"Search failed: {str(e)}"}]

    @staticmethod
    async def get_relevant_content(query: str, url_filter: str = None) -> List[Dict[str, Any]]:
        """
        Get relevant content for a specific query, optionally filtered by URL

        Args:
            query: Search query
            url_filter: Optional URL to filter results

        Returns:
            List of relevant content snippets
        """
        try:
            retrieved_contexts = await retrieval_service.retrieve_relevant_documents(
                query=query,
                url_filter=url_filter
            )

            results = []
            for ctx in retrieved_contexts:
                results.append({
                    "content": ctx.content,
                    "url": ctx.url,
                    "title": ctx.title,
                    "relevance_score": ctx.relevance_score
                })

            logger.info(f"Relevant content retrieved for query: '{query[:50]}...'. Found {len(results)} results.")
            return results

        except Exception as e:
            logger.error(f"Error getting relevant content: {str(e)}")
            return [{"error": f"Content retrieval failed: {str(e)}"}]

    @staticmethod
    async def answer_query(query: str) -> Dict[str, Any]:
        """
        Generate an answer to a user query using the RAG system

        Args:
            query: User query

        Returns:
            Dictionary with answer and sources
        """
        try:
            query_request = QueryRequest(query=query)
            response = await query_service.process_query(query_request)

            result = {
                "answer": response.answer,
                "sources": response.sources,
                "confidence": response.confidence,
                "query_id": response.query_id
            }

            logger.info(f"Query answered successfully: '{query[:50]}...'")
            return result

        except Exception as e:
            logger.error(f"Error answering query: {str(e)}")
            return {
                "answer": f"Sorry, I encountered an error processing your query: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "query_id": None
            }

    @staticmethod
    async def validate_result(result: Dict[str, Any]) -> bool:
        """
        Validate if a result is relevant and accurate

        Args:
            result: Result to validate

        Returns:
            True if result is valid, False otherwise
        """
        try:
            # Basic validation checks
            if not result or not isinstance(result, dict):
                return False

            # Check if it contains an error
            if "error" in result:
                return False

            # Check if answer is substantial
            answer = result.get("answer", "")
            if not answer or len(answer.strip()) < 10:
                return False

            # Check if sources exist and have proper format
            sources = result.get("sources", [])
            if sources and not isinstance(sources, list):
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating result: {str(e)}")
            return False

    @staticmethod
    async def format_context_for_agent(retrieved_contexts: List[Dict[str, Any]], query: str) -> str:
        """
        Format retrieved context for use by the AI agent

        Args:
            retrieved_contexts: List of retrieved context documents
            query: Original user query

        Returns:
            Formatted context string for the agent
        """
        if not retrieved_contexts:
            return "No relevant documents found in the knowledge base."

        formatted_context = "Relevant information from the documentation:\n\n"
        for i, context in enumerate(retrieved_contexts):
            formatted_context += f"Source {i+1} (Relevance: {context.get('relevance_score', 0):.2f}):\n"
            formatted_context += f"Title: {context.get('title', 'N/A')}\n"
            formatted_context += f"URL: {context.get('url', 'N/A')}\n"
            formatted_context += f"Content: {context.get('content', '')}\n\n"

        return formatted_context

    @staticmethod
    async def generate_embedding(text: str) -> List[float]:
        """
        Generate an embedding for the given text

        Args:
            text: Text to generate embedding for

        Returns:
            Embedding vector
        """
        try:
            embedding = await embedding_service.generate_embedding(text)
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    @staticmethod
    async def calculate_similarity_score(query: str, content: str) -> float:
        """
        Calculate similarity score between query and content

        Args:
            query: Query string
            content: Content string

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Generate embeddings for both query and content
            query_embedding = await embedding_service.generate_query_embedding(query)
            content_embedding = await embedding_service.generate_embedding(content)

            # Calculate cosine similarity
            # Simple dot product implementation (in a real system, you'd use a proper similarity function)
            dot_product = sum(a * b for a, b in zip(query_embedding, content_embedding))
            magnitude_a = sum(a * a for a in query_embedding) ** 0.5
            magnitude_b = sum(b * b for b in content_embedding) ** 0.5

            if magnitude_a == 0 or magnitude_b == 0:
                return 0.0

            similarity = dot_product / (magnitude_a * magnitude_b)
            # Normalize to 0-1 range (cosine similarity can be negative)
            normalized_similarity = (similarity + 1) / 2

            return normalized_similarity

        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0

# Create instance of tools for use
rag_tools = RAGTools()