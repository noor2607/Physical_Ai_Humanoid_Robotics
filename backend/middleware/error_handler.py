from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Callable, Awaitable
import logging
import traceback
from config.settings import settings

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """
    Middleware for handling errors and exceptions in the application
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        response = None

        try:
            # Call the next middleware/app in the chain
            response = self.app(scope, receive, send)
            await response
        except HTTPException as e:
            # Handle HTTP exceptions
            await self.handle_http_exception(scope, send, e)
        except Exception as e:
            # Handle all other exceptions
            await self.handle_general_exception(scope, send, request, e)

    async def handle_http_exception(self, scope, send, exc: HTTPException):
        """
        Handle HTTP exceptions

        Args:
            scope: ASGI scope
            send: ASGI send function
            exc: HTTP exception
        """
        # Log the exception
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")

        # Create error response
        response_data = {
            "error": {
                "type": "http_exception",
                "status_code": exc.status_code,
                "message": exc.detail
            }
        }

        # Send response
        await self.send_error_response(scope, send, response_data, exc.status_code)

    async def handle_general_exception(self, scope, send, request: Request, exc: Exception):
        """
        Handle general exceptions

        Args:
            scope: ASGI scope
            send: ASGI send function
            request: Request object
            exc: Exception
        """
        # Log the exception with traceback
        error_msg = f"General Exception: {str(exc)}"
        if settings.debug:
            error_msg += f"\nTraceback: {traceback.format_exc()}"

        logger.error(error_msg)

        # Create error response
        response_data = {
            "error": {
                "type": "general_exception",
                "message": "An internal server error occurred"
            }
        }

        # In debug mode, include more details
        if settings.debug:
            response_data["error"]["details"] = str(exc)
            response_data["error"]["traceback"] = traceback.format_exc()

        # Send response
        await self.send_error_response(scope, send, response_data, 500)

    async def send_error_response(self, scope, send, response_data: dict, status_code: int):
        """
        Send error response

        Args:
            scope: ASGI scope
            send: ASGI send function
            response_data: Error response data
            status_code: HTTP status code
        """
        # Create response
        response = JSONResponse(
            content=response_data,
            status_code=status_code
        )

        # Set scope for response
        scope["app"] = self.app

        # Send response
        await response(scope, receive, send)

# Function to add error handling middleware to FastAPI app
def add_error_handler(app):
    """
    Add error handling middleware to FastAPI application

    Args:
        app: FastAPI application instance
    """
    # Wrap the app with our middleware
    app.middleware_instance = ErrorHandlerMiddleware(app)

    # Replace the app's __call__ method with our middleware's __call__ method
    original_call = app.__call__

    async def middleware_call(scope, receive, send):
        if scope["type"] != "http":
            await original_call(scope, receive, send)
            return

        # Use our middleware for HTTP requests
        await app.middleware_instance(scope, receive, send)

    app.__call__ = middleware_call
    return app

# Alternative implementation using FastAPI's built-in exception handlers
def setup_exception_handlers(app):
    """
    Set up FastAPI's built-in exception handlers

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException):
        logger.warning(f"404 error: {request.url}")
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "type": "not_found",
                    "message": "The requested resource was not found"
                }
            }
        )

    @app.exception_handler(500)
    async def internal_error_handler(request: Request, exc: HTTPException):
        logger.error(f"500 error: {str(exc)}")
        error_content = {
            "error": {
                "type": "internal_server_error",
                "message": "An internal server error occurred"
            }
        }

        if settings.debug:
            error_content["error"]["details"] = str(exc)

        return JSONResponse(
            status_code=500,
            content=error_content
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        if settings.debug:
            logger.error(f"Traceback: {traceback.format_exc()}")

        error_content = {
            "error": {
                "type": "general_exception",
                "message": "An unexpected error occurred"
            }
        }

        if settings.debug:
            error_content["error"]["details"] = str(exc)
            error_content["error"]["traceback"] = traceback.format_exc()

        return JSONResponse(
            status_code=500,
            content=error_content
        )

    return app