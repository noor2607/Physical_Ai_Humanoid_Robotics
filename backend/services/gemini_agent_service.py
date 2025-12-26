import asyncio
from google import genai
from google.genai import types
from typing import Dict, Any, List, Optional
from config.settings import settings
from tools.qdrant_search_tool import qdrant_search_tool
import logging
import json

logger = logging.getLogger(__name__)

class GeminiAgentService:
    """
    Agent service using Google Gen AI with Qdrant content search using proper function calling
    """

    def __init__(self):
        # Use a free/generic model if available, otherwise fall back to a paid model
        # Using gemini-1.5-flash which is typically more available in free tier
        try:
            self.model_name = 'gemini-2.5-flash'  # Updated to newer model
        except:
            try:
                self.model_name = 'gemini-1.5-flash'  # Fallback
            except:
                self.model_name = 'gemini-pro'  # Last fallback

        # Create the client instance with API key
        self.client = genai.Client(api_key=settings.gemini_api_key)

        # Create an agent-like interface following best practices with proper system instructions
        self.system_instruction = """
        You are an AI assistant helping users with the AI Textbook documentation on Physical AI & Humanoid Robotics.
        When a user asks a question about the textbook content (e.g., about ROS2, Simulation, Isaac, VLA, robotics topics),
        you MUST use the search_book_content function to find relevant information in the textbook.
        Always provide specific citations to the sources you use from the textbook.
        Be helpful, accurate, and concise in your responses.
        If you cannot find the information in the provided context, clearly state that the information is not available in the textbook.
        For simple greetings or general questions not related to the textbook, provide friendly responses without using search functions.
        IMPORTANT: For any technical question about robotics, AI, or the textbook topics, you MUST use the search function first.
        """

    def create_search_tool(self):
        """
        Create a proper function declaration for searching book content in Qdrant
        """
        function = types.FunctionDeclaration(
            name='search_book_content',
            description='Search the book content in Qdrant vector database for relevant information',
            parameters_json_schema={
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'Search query to find relevant content'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of results to return (default: 5)',
                        'default': 5
                    },
                    'url_filter': {
                        'type': 'string',
                        'description': 'Optional URL filter to narrow search scope'
                    }
                },
                'required': ['query']
            }
        )

        tool = types.Tool(function_declarations=[function])
        return tool

    async def run_query(self, query: str) -> Dict[str, Any]:
        """
        Run a query through the agent system using proper function calling

        Args:
            query: User query to process

        Returns:
            Dictionary with response and sources
        """
        try:
            logger.info(f"Processing query through Gemini agent: '{query[:50]}...'")

            # For simple queries like "hello", respond directly without search
            simple_queries = ["hello", "hi", "hey", "greetings", "help", "what can you do"]
            if query.lower().strip() in simple_queries or len(query.strip()) < 3:
                simple_responses = {
                    "hello": "Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook. I can help you find information about ROS2, Simulation, Isaac, VLA, and other robotics topics. What would you like to know?",
                    "hi": "Hi there! I'm here to help you with the Physical AI & Humanoid Robotics textbook. Ask me anything about the content!",
                    "hey": "Hey! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook. Feel free to ask me questions about the material.",
                    "greetings": "Greetings! I'm here to assist you with the Physical AI & Humanoid Robotics textbook. What can I help you with today?",
                    "help": "I can help you find information in the Physical AI & Humanoid Robotics textbook. Ask me about ROS2, Simulation, Isaac, VLA, or any other topic from the textbook.",
                    "what can you do": "I can help you find and explain content from the Physical AI & Humanoid Robotics textbook. I can search for specific topics, explain concepts, and provide citations to the relevant materials."
                }

                response_text = simple_responses.get(query.lower().strip(),
                    f"Hello! I can help you with information from the Physical AI & Humanoid Robotics textbook. What would you like to know about?")

                return {
                    "answer": response_text,
                    "sources": [],
                    "confidence": 0.8,  # High confidence for simple responses
                    "query": query
                }

            # Create the search tool
            search_tool = self.create_search_tool()

            # Configure the generation with tools and force function calling for textbook queries
            # For technical questions about robotics, AI, etc., we want to ensure search is used
            should_search = any(keyword in query.lower() for keyword in ['ros2', 'simulation', 'isaac', 'vla', 'robotics', 'ai', 'robot', 'physics', 'gazebo', 'unity', 'perception', 'manipulation', 'planning', 'control'])

            if should_search:
                # Force function calling for technical queries
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=[search_tool],
                    tool_config=types.ToolConfig(
                        function_calling_config=types.FunctionCallingConfig(
                            mode='ANY'  # ANY forces the model to call at least one function if possible
                        )
                    ),
                    temperature=0.3,
                    max_output_tokens=800
                )
            else:
                # For simple queries like greetings, don't force function calling
                config = types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    tools=[search_tool],
                    temperature=0.3,
                    max_output_tokens=800
                )

            # Create the content for the model
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(text=query)
                    ]
                )
            ]

            # Generate content with automatic function calling
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            # Process the response to extract sources and handle function calls
            sources = []
            response_text = ""

            if hasattr(response, 'text') and response.text:
                response_text = response.text.strip()
            else:
                response_text = f"I processed your query but couldn't generate a proper response: {query}"

            # Extract any function calls that were made
            if hasattr(response, 'function_calls') and response.function_calls:
                for function_call in response.function_calls:
                    if function_call.name == 'search_book_content':
                        # Extract arguments
                        args = function_call.args
                        query_arg = args.get('query', query)
                        limit_arg = args.get('limit', 3)

                        # Perform the actual search
                        search_results = await qdrant_search_tool.search_book_content(query_arg, limit_arg)

                        if search_results and not (len(search_results) == 1 and "error" in search_results[0]):
                            # Format the context from search results
                            context_parts = []
                            for result in search_results:
                                if "error" not in result:
                                    context_parts.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {result['content'][:500]}...")

                            context = "\n\n".join(context_parts)

                            # Create a new request with the context
                            enhanced_contents = [
                                types.Content(
                                    role="user",
                                    parts=[
                                        types.Part.from_text(text=f"{query}\n\nHere is relevant context from the textbook:\n{context}")
                                    ]
                                )
                            ]

                            # Generate final response with context
                            final_response = self.client.models.generate_content(
                                model=self.model_name,
                                contents=enhanced_contents,
                                config=types.GenerateContentConfig(
                                    system_instruction=self.system_instruction,
                                    temperature=0.3,
                                    max_output_tokens=800
                                )
                            )

                            if hasattr(final_response, 'text') and final_response.text:
                                response_text = final_response.text.strip()

                            # Extract sources from search results
                            sources = [
                                {
                                    "title": result["title"],
                                    "url": result["url"],
                                    "relevance_score": result["relevance_score"]
                                }
                                for result in search_results if "error" not in result
                            ]

            # If no sources were found but response was generated, it might be a general response
            if not sources and "couldn't find" in response_text.lower():
                # Retry with the search tool to make sure
                search_results = await qdrant_search_tool.search_book_content(query, limit=3)

                if search_results and not (len(search_results) == 1 and "error" in search_results[0]):
                    # Extract sources from search results
                    sources = [
                        {
                            "title": result["title"],
                            "url": result["url"],
                            "relevance_score": result["relevance_score"]
                        }
                        for result in search_results if "error" not in result
                    ]

                    # If sources found, update response to be more positive
                    if sources and f"couldn't find relevant information in the textbook about: {query}" in response_text:
                        # Generate a new response that acknowledges the found sources
                        context_parts = []
                        for result in search_results:
                            if "error" not in result:
                                context_parts.append(f"Source: {result['title']}\nURL: {result['url']}\nContent: {result['content'][:500]}...")

                        context = "\n\n".join(context_parts)

                        enhanced_contents = [
                            types.Content(
                                role="user",
                                parts=[
                                    types.Part.from_text(text=f"{query}\n\nHere is relevant context from the textbook:\n{context}")
                                ]
                            )
                        ]

                        # Generate final response with context
                        final_response = self.client.models.generate_content(
                            model=self.model_name,
                            contents=enhanced_contents,
                            config=types.GenerateContentConfig(
                                system_instruction=self.system_instruction,
                                temperature=0.3,
                                max_output_tokens=800
                            )
                        )

                        if hasattr(final_response, 'text') and final_response.text:
                            response_text = final_response.text.strip()

            # Calculate confidence based on relevance scores
            if sources:
                avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources)
                confidence = min(avg_relevance, 1.0)
            else:
                # For simple responses or when no sources were found, return appropriate confidence
                if query.lower().strip() in simple_queries:
                    confidence = 0.8
                else:
                    confidence = 0.1

            result = {
                "answer": response_text,
                "sources": sources,
                "confidence": confidence,
                "query": query
            }

            logger.info(f"Query processed successfully: '{query[:50]}...'")
            return result

        except Exception as e:
            logger.error(f"Error processing query '{query[:50]}...': {str(e)}")
            # For simple queries, provide a friendly response even if there's an error
            simple_queries = ["hello", "hi", "hey", "greetings"]
            if query.lower().strip() in simple_queries:
                return {
                    "answer": "Hello! I'm your AI assistant for the Physical AI & Humanoid Robotics textbook. I'm having some technical issues right now, but normally I can help you find information about ROS2, Simulation, Isaac, VLA, and other robotics topics. What would you like to know?",
                    "sources": [],
                    "confidence": 0.5,
                    "query": query
                }
            else:
                return {
                    "answer": f"Sorry, I encountered an error processing your query: {str(e)}",
                    "sources": [],
                    "confidence": 0.0,
                    "query": query
                }

    async def get_agent_capabilities(self) -> Dict[str, Any]:
        """
        Get the capabilities of the agent system
        """
        return {
            "name": "AI Textbook RAG Agent with Google Gen AI",
            "version": "2.0.0",
            "model": self.model_name,
            "capabilities": [
                "Book content search in Qdrant using function calling",
                "Semantic retrieval with proper RAG",
                "Source attribution",
                "Context-aware responses",
                "Automatic function calling",
                "Simple greeting handling"
            ],
            "available_tools": ["search_book_content"],
            "description": "An AI agent for answering questions about AI textbook documentation using RAG technology with Google Gen AI and proper function calling"
        }

# Global instance of the agent service
gemini_agent_service = GeminiAgentService()