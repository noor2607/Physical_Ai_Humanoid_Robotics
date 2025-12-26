from typing import List, Dict, Optional
from config.settings import settings
from services.gemini_embedding import gemini_embedding_service
from services.vector_store import vector_store_service
from models.retrieved_context import RetrievedContext, RetrievedContextResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

class GeminiRetrievalService:
    """
    Service for retrieving relevant documents based on semantic similarity using Gemini embeddings
    """

    def __init__(self):
        pass

    async def retrieve_relevant_documents(
        self,
        query: str,
        limit: int = None,
        url_filter: Optional[str] = None
    ) -> List[RetrievedContextResponse]:
        """
        Retrieve relevant documents for a given query using Gemini embeddings

        Args:
            query: User query string
            limit: Maximum number of results to return (defaults to settings)
            url_filter: Optional filter to search within specific URL

        Returns:
            List of RetrievedContextResponse objects
        """
        if limit is None:
            limit = settings.max_results

        try:
            # Generate embedding for the query using Gemini
            query_embedding = await gemini_embedding_service.generate_query_embedding(query)

            # Search for relevant documents in vector store
            search_results = vector_store_service.search_documents(
                query_embedding=query_embedding,
                limit=limit,
                url_filter=url_filter
            )

            # Convert results to RetrievedContextResponse objects
            retrieved_contexts = []
            for i, result in enumerate(search_results):
                retrieved_context = RetrievedContextResponse(
                    id=result["id"],
                    content=result["content"],
                    url=result["url"],
                    title=result["title"],
                    relevance_score=result["similarity_score"],
                    rank=i + 1
                )
                retrieved_contexts.append(retrieved_context)

            logger.info(f"Retrieved {len(retrieved_contexts)} relevant documents for query: '{query[:50]}...'")
            return retrieved_contexts

        except Exception as e:
            logger.error(f"Error retrieving documents for query '{query[:50]}...': {str(e)}")
            raise

    def rank_documents_by_relevance(
        self,
        documents: List[RetrievedContextResponse],
        query: str
    ) -> List[RetrievedContextResponse]:
        """
        Additional ranking of documents based on relevance to the query

        Args:
            documents: List of retrieved documents
            query: Original query for relevance comparison

        Returns:
            List of documents ranked by relevance
        """
        # In this implementation, the vector store already ranks by semantic similarity
        # Additional ranking could be implemented based on other factors like:
        # - keyword matching
        # - document recency
        # - source authority
        # For now, we'll return the documents as they are already ranked by the vector store
        return documents

    def format_context_for_agent(
        self,
        retrieved_contexts: List[RetrievedContextResponse],
        query: str
    ) -> str:
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
            formatted_context += f"Source {i+1} (Relevance: {context.relevance_score:.2f}):\n"
            formatted_context += f"Title: {context.title}\n"
            formatted_context += f"URL: {context.url}\n"
            formatted_context += f"Content: {context.content}\n\n"

        return formatted_context

    def deduplicate_results(
        self,
        retrieved_contexts: List[RetrievedContextResponse]
    ) -> List[RetrievedContextResponse]:
        """
        Remove duplicate or highly similar results

        Args:
            retrieved_contexts: List of retrieved context documents

        Returns:
            List of deduplicated context documents
        """
        seen_content = set()
        unique_contexts = []

        for context in retrieved_contexts:
            # Create a hash of the content to identify duplicates
            content_hash = hash(context.content.strip().lower())

            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_contexts.append(context)

        logger.info(f"Deduplicated results from {len(retrieved_contexts)} to {len(unique_contexts)} unique documents")
        return unique_contexts

    async def search_and_rank(
        self,
        query: str,
        limit: int = None,
        url_filter: Optional[str] = None,
        deduplicate: bool = True
    ) -> List[RetrievedContextResponse]:
        """
        Complete search and ranking pipeline using Gemini embeddings

        Args:
            query: User query string
            limit: Maximum number of results to return
            url_filter: Optional filter to search within specific URL
            deduplicate: Whether to remove duplicate results

        Returns:
            List of ranked, relevant context documents
        """
        # Retrieve relevant documents
        retrieved_contexts = await self.retrieve_relevant_documents(
            query=query,
            limit=limit,
            url_filter=url_filter
        )

        # Deduplicate if requested
        if deduplicate:
            retrieved_contexts = self.deduplicate_results(retrieved_contexts)

        # Rank by relevance (already done by vector store, but can apply additional ranking)
        ranked_contexts = self.rank_documents_by_relevance(retrieved_contexts, query)

        logger.info(f"Search and rank pipeline returned {len(ranked_contexts)} results for query: '{query[:50]}...'")
        return ranked_contexts

    def get_context_snippet(
        self,
        content: str,
        query: str,
        snippet_length: int = 200
    ) -> str:
        """
        Extract a relevant snippet from content based on the query

        Args:
            content: Full content to extract snippet from
            query: Query to match against
            snippet_length: Length of the snippet to extract

        Returns:
            Relevant snippet from the content
        """
        # Simple implementation: find the first occurrence of query-related terms
        import re

        # Split query into words for matching
        query_words = query.lower().split()

        # Find the position of the first query word in the content
        content_lower = content.lower()
        start_pos = len(content)  # Initialize to end of content
        for word in query_words:
            pos = content_lower.find(word)
            if pos != -1 and pos < start_pos:
                start_pos = pos

        # If no query word found, return the beginning of the content
        if start_pos == len(content):
            start_pos = 0

        # Extract snippet around the found position
        snippet_start = max(0, start_pos - snippet_length // 2)
        snippet_end = min(len(content), snippet_start + snippet_length)

        # Adjust to word boundaries if possible
        if snippet_start > 0:
            # Move to the beginning of the word
            while snippet_start > 0 and content[snippet_start - 1].isalnum():
                snippet_start -= 1

        if snippet_end < len(content):
            # Move to the end of the word
            while snippet_end < len(content) and content[snippet_end - 1].isalnum():
                snippet_end += 1

        snippet = content[snippet_start:snippet_end].strip()

        # Add ellipsis if we truncated
        if snippet_start > 0:
            snippet = "..." + snippet
        if snippet_end < len(content):
            snippet = snippet + "..."

        return snippet

# Global instance of the Gemini retrieval service
gemini_retrieval_service = GeminiRetrievalService()