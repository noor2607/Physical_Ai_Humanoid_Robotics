import asyncio
import json
from typing import Dict, Any, List, Optional
from config.settings import settings
import logging
from tools.rag_tools import rag_tools
from models.query import QueryRequest, QueryResponse
from services.query_service import query_service
from google import genai

logger = logging.getLogger(__name__)

class AgentService:
    """
    Service for integrating with OpenAI Agent SDK and managing agent interactions
    """

    def __init__(self):
        # Store API key for later use - initialize client when needed to avoid connection issues
        self.api_key = settings.gemini_api_key
        self.model_name = 'gemini-1.5-flash'  # Use a more available model
        self.tools = {
            "search_documentation": {
                "type": "function",
                "function": {
                    "name": "search_documentation",
                    "description": "Search the documentation database for relevant content",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "limit": {"type": "integer", "description": "Maximum number of results to return", "default": 5}
                        },
                        "required": ["query"]
                    }
                }
            },
            "get_relevant_content": {
                "type": "function",
                "function": {
                    "name": "get_relevant_content",
                    "description": "Get relevant content for a specific query, optionally filtered by URL",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "url_filter": {"type": "string", "description": "Optional URL to filter results", "default": None}
                        },
                        "required": ["query"]
                    }
                }
            },
            "answer_query": {
                "type": "function",
                "function": {
                    "name": "answer_query",
                    "description": "Generate an answer to a user query using the RAG system",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "User query"}
                        },
                        "required": ["query"]
                    }
                }
            }
        }

    async def create_agent_session(self, initial_context: str = "") -> str:
        """
        Create a new agent session with initial context

        Args:
            initial_context: Initial context for the agent session

        Returns:
            Session ID for the agent session
        """
        # In a real implementation, this would create a proper agent session
        # For now, we'll return a placeholder
        import uuid
        session_id = str(uuid.uuid4())
        logger.info(f"Created new agent session: {session_id}")
        return session_id

    async def process_agent_request(self, query: str, session_id: str = None) -> Dict[str, Any]:
        """
        Process a request through the agent system

        Args:
            query: User query
            session_id: Optional session ID for maintaining conversation context

        Returns:
            Dictionary with agent response
        """
        try:
            logger.info(f"Processing agent request: '{query[:50]}...'")

            # For now, we'll use the existing query service
            # In a full implementation, this would involve the agent calling tools
            query_request = QueryRequest(query=query, session_id=session_id)
            response = await query_service.process_query(query_request)

            result = {
                "query_id": response.query_id,

                "answer": response.answer,
                "sources": response.sources,
                "confidence": response.confidence,
                "session_id": session_id
            }

            logger.info(f"Agent request processed successfully: '{query[:50]}...'")
            return result

        except Exception as e:
            logger.error(f"Error processing agent request: {str(e)}")
            return {
                "answer": f"Sorry, I encountered an error processing your request: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "session_id": session_id
            }

    async def call_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Call a specific tool with given parameters

        Args:
            tool_name: Name of the tool to call
            parameters: Parameters for the tool

        Returns:
            Result of the tool call
        """
        try:
            if tool_name == "search_documentation":
                query = parameters.get("query")
                limit = parameters.get("limit", 5)
                return await rag_tools.search_documentation(query, limit)
            elif tool_name == "get_relevant_content":
                query = parameters.get("query")
                url_filter = parameters.get("url_filter")
                return await rag_tools.get_relevant_content(query, url_filter)
            elif tool_name == "answer_query":
                query = parameters.get("query")
                return await rag_tools.answer_query(query)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return {"error": f"Tool call failed: {str(e)}"}

    async def generate_agent_response(self, query: str, tools_to_use: List[str] = None) -> str:
        """
        Generate a response using the agent with specified tools

        Args:
            query: User query
            tools_to_use: List of tools to use (if None, use all available)

        Returns:
            Generated response
        """
        try:
            # If no specific tools are specified, use all available tools
            if tools_to_use is None:
                tools_to_use = list(self.tools.keys())

            # In a real implementation, this would involve calling the agent SDK
            # For now, we'll simulate by using our tools directly
            results = []
            for tool_name in tools_to_use:
                if tool_name in self.tools:
                    # Call the tool with the query
                    result = await self.call_tool(tool_name, {"query": query})
                    results.append({
                        "tool": tool_name,
                        "result": result
                    })

            # Combine results and generate final response using Gemini
            # Format the context from the tool results
            context_parts = []
            for result in results:
                tool_name = result["tool"]
                tool_result = result["result"]
                context_parts.append(f"Tool '{tool_name}' result: {tool_result}")

            context = "\n".join(context_parts)

            # Construct the prompt for Gemini
            prompt = f"""
            You are an AI assistant helping users with the AI Textbook documentation.
            Use the information from the tools below to answer the user's question.
            If the tools don't contain the information needed to answer the question,
            clearly state that the information is not available in the documentation.

            Tool Results:
            {context}

            User Question:
            {query}

            Please provide a helpful and accurate answer based on the tool results.
            """

            # Use Google Gen AI API to generate response
            import google.genai as genai_client
            from google.genai import types

            client = genai_client.Client(api_key=self.api_key)
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
            logger.error(f"Error generating agent response: {str(e)}")
            return f"Sorry, I encountered an error generating a response: {str(e)}"

    async def manage_conversation_memory(self, session_id: str, query: str, response: str) -> bool:
        """
        Manage conversation memory for the agent

        Args:
            session_id: Session ID for the conversation
            query: User query
            response: Agent response

        Returns:
            True if memory was updated successfully
        """
        # In a real implementation, this would manage conversation history
        # For now, we'll just log the interaction
        logger.info(f"Conversation memory updated for session {session_id}: Query: '{query[:50]}...', Response: '{response[:50]}...'")
        return True

    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the agent system

        Returns:
            Dictionary with agent capabilities
        """
        return {
            "name": "AI Textbook RAG Agent",
            "version": "1.0.0",
            "capabilities": [
                "Documentation search",
                "Content retrieval",
                "Query answering",
                "Source attribution"
            ],
            "available_tools": list(self.tools.keys()),
            "description": "An AI agent for answering questions about AI textbook documentation using RAG technology"
        }

# Global instance of the agent service
agent_service = AgentService()
