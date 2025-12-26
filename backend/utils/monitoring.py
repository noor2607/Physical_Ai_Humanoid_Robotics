import logging
from datetime import datetime
from typing import Dict, Any, Optional
import time
from config.settings import settings

# Set up logger for monitoring
logger = logging.getLogger(__name__)

class MonitoringService:
    """
    Service for monitoring and logging application metrics
    """

    def __init__(self):
        self.metrics: Dict[str, Any] = {}
        self.start_time = datetime.utcnow()

    def log_request(self, endpoint: str, method: str, duration: float, status_code: int):
        """
        Log API request metrics

        Args:
            endpoint: API endpoint
            method: HTTP method
            duration: Request duration in seconds
            status_code: HTTP status code
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "endpoint": endpoint,
            "method": method,
            "duration": duration,
            "status_code": status_code
        }

        level = logging.INFO if status_code < 400 else logging.WARNING
        logger.log(level, f"API Request: {method} {endpoint} - {status_code} in {duration:.3f}s")

    def log_query_performance(self, query: str, duration: float, results_count: int):
        """
        Log query performance metrics

        Args:
            query: Query string
            duration: Query duration in seconds
            results_count: Number of results returned
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query[:100] + "..." if len(query) > 100 else query,  # Truncate long queries
            "duration": duration,
            "results_count": results_count
        }

        logger.info(f"Query Performance: '{query[:50]}...' took {duration:.3f}s, returned {results_count} results")

    def log_ingestion_performance(self, sitemap_url: str, pages_processed: int, duration: float):
        """
        Log ingestion performance metrics

        Args:
            sitemap_url: URL of the sitemap being processed
            pages_processed: Number of pages processed
            duration: Processing duration in seconds
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "sitemap_url": sitemap_url,
            "pages_processed": pages_processed,
            "duration": duration
        }

        logger.info(f"Ingestion Performance: Processed {pages_processed} pages from {sitemap_url} in {duration:.2f}s")

    def get_system_uptime(self) -> float:
        """
        Get system uptime in seconds

        Returns:
            Uptime in seconds
        """
        uptime = (datetime.utcnow() - self.start_time).total_seconds()
        return uptime

    def get_system_metrics(self) -> Dict[str, Any]:
        """
        Get system metrics

        Returns:
            Dictionary with system metrics
        """
        metrics = {
            "uptime_seconds": self.get_system_uptime(),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "running",
            "settings": {
                "debug": settings.debug,
                "log_level": settings.log_level,
                "max_query_length": settings.max_query_length,
                "max_results": settings.max_results
            }
        }

        return metrics

    def log_error(self, error: Exception, context: str = ""):
        """
        Log error with context

        Args:
            error: Exception object
            context: Context of the error
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(error),
            "context": context,
            "type": type(error).__name__
        }

        logger.error(f"Error in {context}: {type(error).__name__} - {str(error)}")

    def log_info(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log informational message

        Args:
            message: Message to log
            extra: Additional data to log
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }

        if extra:
            log_data.update(extra)

        logger.info(message)

    def log_warning(self, message: str, extra: Optional[Dict[str, Any]] = None):
        """
        Log warning message

        Args:
            message: Warning message
            extra: Additional data to log
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message
        }

        if extra:
            log_data.update(extra)

        logger.warning(message)

    def time_function(self, func_name: str):
        """
        Decorator to time function execution

        Args:
            func_name: Name of the function being timed
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    self.log_info(f"{func_name} executed in {duration:.3f}s")
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    self.log_error(e, f"{func_name} execution after {duration:.3f}s")
                    raise
            return wrapper
        return decorator

# Global instance of monitoring service
monitoring_service = MonitoringService()

# Context manager for timing operations
class Timer:
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            if exc_type is None:
                monitoring_service.log_info(f"{self.operation_name} completed in {duration:.3f}s")
            else:
                monitoring_service.log_error(
                    exc_val,
                    f"{self.operation_name} failed after {duration:.3f}s"
                )