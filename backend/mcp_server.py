import asyncio
import json
from typing import Dict, Any, List
from fastapi import WebSocket, WebSocketDisconnect
import logging
from config.settings import settings
from services.retrieval import retrieval_service
from services.query_service import query_service
from models.query import QueryRequest

logger = logging.getLogger(__name__)

class MCPServer:
    """
    MCP (Model Context Protocol) server implementation for the RAG system
    This allows the OpenAI Agent to access the RAG system's capabilities
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.tools = {
            "search_documentation": self.search_documentation,
            "get_relevant_content": self.get_relevant_content,
            "answer_query": self.answer_query,
        }

    async def register_connection(self, websocket: WebSocket):
        """
        Register a new WebSocket connection
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New MCP connection established. Total connections: {len(self.active_connections)}")

    def disconnect_connection(self, websocket: WebSocket):
        """
        Remove a WebSocket connection
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"MCP connection closed. Total connections: {len(self.active_connections)}")

    async def broadcast_message(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected clients
        """
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {str(e)}")
                self.disconnect_connection(connection)

    async def search_documentation(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search the documentation database for relevant content

        Args:
            query: Search query
            limit: Maximum number of results to return

        Returns:
            List of relevant documents with metadata
        """
        try:
            # Convert the query to a QueryRequest object
            query_request = QueryRequest(query=query)

            # Retrieve relevant documents
            retrieved_contexts = await retrieval_service.search_and_rank(
                query=query,
                limit=limit
            )

            # Format results
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
            return []

    async def get_relevant_content(self, query: str, url_filter: str = None) -> List[Dict[str, Any]]:
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
            return []

    async def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Generate an answer to a user query using the RAG system

        Args:
            query: User query

        Returns:
            Dictionary with answer and sources
        """
        try:
            # Create a query request
            query_request = QueryRequest(query=query)

            # Process the query through the RAG system
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

    async def handle_request(self, websocket: WebSocket, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming MCP request

        Args:
            websocket: WebSocket connection
            data: Request data

        Returns:
            Response to send back to the client
        """
        try:
            # Parse the request
            request_type = data.get("type")
            tool_name = data.get("tool")
            parameters = data.get("parameters", {})

            if request_type == "tool_call":
                if tool_name in self.tools:
                    # Call the appropriate tool
                    result = await self.tools[tool_name](**parameters)
                    return {
                        "type": "tool_response",
                        "request_id": data.get("request_id"),
                        "result": result
                    }
                else:
                    return {
                        "type": "error",
                        "request_id": data.get("request_id"),
                        "error": f"Unknown tool: {tool_name}"
                    }

            elif request_type == "list_tools":
                # Return available tools
                tool_list = []
                for name, func in self.tools.items():
                    # In a real implementation, you would have proper tool descriptions
                    tool_list.append({
                        "name": name,
                        "description": f"Tool for {name.replace('_', ' ')}"
                    })

                return {
                    "type": "tool_list",
                    "request_id": data.get("request_id"),
                    "tools": tool_list
                }

            else:
                return {
                    "type": "error",
                    "request_id": data.get("request_id"),
                    "error": f"Unknown request type: {request_type}"
                }

        except Exception as e:
            logger.error(f"Error handling MCP request: {str(e)}")
            return {
                "type": "error",
                "request_id": data.get("request_id"),
                "error": str(e)
            }

    async def handle_websocket(self, websocket: WebSocket):
        """
        Handle WebSocket connection for MCP protocol
        """
        await self.register_connection(websocket)

        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                request_data = json.loads(data)

                # Handle the request
                response = await self.handle_request(websocket, request_data)

                # Send response back to client
                await websocket.send_text(json.dumps(response))

        except WebSocketDisconnect:
            logger.info("MCP WebSocket disconnected")
        except json.JSONDecodeError:
            logger.error("Invalid JSON received from MCP client")
        except Exception as e:
            logger.error(f"Error in MCP WebSocket handler: {str(e)}")
        finally:
            self.disconnect_connection(websocket)

# Global instance of the MCP server
mcp_server = MCPServer()