from typing import List, Dict, Optional
from datetime import datetime
import logging
from config.settings import settings
from services.retrieval import retrieval_service
from services.embedding import embedding_service
from models.query import Query, QueryRequest, QueryResponse, QueryResult
from models.retrieved_context import RetrievedContextResponse
import asyncio
import time
from google import genai

logger = logging.getLogger(__name__)

class QueryService:
    """
    Service for processing user queries and generating responses
    """

    def __init__(self):
        # Use the Gemini Pro model for response generation
        # We'll initialize the client when needed to avoid connection issues
        self.model_name = 'gemini-1.5-flash'  # Use a more available model

    async def process_query(self, query_request: QueryRequest) -> QueryResponse:
        """
        Process a user query and generate a response

        Args:
            query_request: QueryRequest object containing the user query and session info

        Returns:
            QueryResponse object with the answer and sources
        """
        start_time = time.time()

        try:
            # Validate query length
            if len(query_request.query) > settings.max_query_length:
                raise ValueError(f"Query exceeds maximum length of {settings.max_query_length} characters")

            # Create query object
            query_obj = Query(
                user_input=query_request.query,
                session_id=query_request.session_id,
                timestamp=datetime.utcnow()
            )

            # Retrieve relevant documents
            retrieved_contexts = await retrieval_service.search_and_rank(
                query=query_request.query,
                limit=settings.max_results
            )

            # Format context for the language model
            formatted_context = retrieval_service.format_context_for_agent(
                retrieved_contexts,
                query_request.query
            )

            # Generate response using the language model
            response_text = await self._generate_response(
                query_request.query,
                formatted_context
            )

            # Calculate response confidence based on context relevance
            confidence = self._calculate_confidence(retrieved_contexts)

            # Prepare sources for response
            sources = self._prepare_sources(retrieved_contexts)

            # Create query response
            query_response = QueryResponse(
                query_id=query_obj.id,
                answer=response_text,
                sources=sources,
                confidence=confidence
            )

            # Update query object with response
            query_obj.response_generated = response_text
            query_obj.retrieved_context_ids = [ctx.id for ctx in retrieved_contexts]

            processing_time = time.time() - start_time
            logger.info(f"Processed query in {processing_time:.2f}s: '{query_request.query[:50]}...'")

            return query_response

        except Exception as e:
            logger.error(f"Error processing query '{query_request.query[:50]}...': {str(e)}")
            raise

    async def _generate_response(self, query: str, context: str) -> str:
        """
        Generate a response using the language model with the provided context

        Args:
            query: User query
            context: Relevant context from documentation

        Returns:
            Generated response text
        """
        try:
            # Import the client here to avoid initialization issues
            from google import genai as genai_client
            from google.genai import types

            # Construct the prompt for the language model
            prompt = f"""
            You are an AI assistant helping users with the AI Textbook documentation.
            Use only the information provided in the context below to answer the user's question.
            If the context doesn't contain the information needed to answer the question,
            clearly state that the information is not available in the documentation.

            Context:
            {context}

            User Question:
            {query}

            Please provide a helpful and accurate answer based on the documentation.
            """

            # Use Google Gen AI API to generate response
            client = genai_client.Client(api_key=settings.gemini_api_key)
            response = client.models.generate_content(
                model=self.model_name,
                contents=[
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_text(text=prompt)
                        ]
                    )
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=500,
                    temperature=0.3,
                )
            )

            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            else:
                return f"I processed your query but couldn't generate a proper response: {query}"

        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Return a default response if generation fails
            return f"I encountered an error while generating a response. The documentation may not contain information about: {query}"

    def _calculate_confidence(self, retrieved_contexts: List[RetrievedContextResponse]) -> float:
        """
        Calculate confidence score based on the relevance of retrieved documents

        Args:
            retrieved_contexts: List of retrieved context documents

        Returns:
            Confidence score between 0.0 and 1.0
        """
        if not retrieved_contexts:
            return 0.1  # Low confidence if no context found

        # Calculate average relevance score
        total_relevance = sum(ctx.relevance_score for ctx in retrieved_contexts)
        avg_relevance = total_relevance / len(retrieved_contexts)

        # Adjust confidence based on number of sources and their relevance
        num_sources_factor = min(len(retrieved_contexts) / settings.max_results, 1.0)

        # Weight relevance more heavily than number of sources
        confidence = (avg_relevance * 0.7) + (num_sources_factor * 0.3)

        return min(confidence, 1.0)  # Ensure confidence doesn't exceed 1.0

    def _prepare_sources(self, retrieved_contexts: List[RetrievedContextResponse]) -> List[Dict]:
        """
        Prepare sources for the response

        Args:
            retrieved_contexts: List of retrieved context documents

        Returns:
            List of source dictionaries
        """
        sources = []
        for ctx in retrieved_contexts:
            source = {
                "url": ctx.url,
                "title": ctx.title,
                "relevance_score": ctx.relevance_score
            }
            sources.append(source)

        return sources

    async def validate_query(self, query: str) -> bool:
        """
        Validate that a query is appropriate for processing

        Args:
            query: Query string to validate

        Returns:
            True if query is valid, False otherwise
        """
        if not query or not query.strip():
            return False

        if len(query.strip()) < 3:
            return False

        # Check for potentially harmful content (basic check)
        harmful_keywords = ["drop table", "delete from", "exec(", "eval("]
        query_lower = query.lower()
        for keyword in harmful_keywords:
            if keyword in query_lower:
                return False

        return True

    async def get_query_statistics(self, session_id: str) -> Dict:
        """
        Get statistics for queries in a session

        Args:
            session_id: ID of the session to get statistics for

        Returns:
            Dictionary with query statistics
        """
        # In a real implementation, this would query a database
        # For now, return placeholder data
        return {
            "session_id": session_id,
            "total_queries": 0,
            "avg_response_time": 0.0,
            "most_common_topics": [],
            "satisfaction_score": 0.0
        }

# Global instance of the query service
query_service = QueryService()