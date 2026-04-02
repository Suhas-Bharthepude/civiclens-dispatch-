# backend/app/middleware.py
# Request logging middleware for FastAPI
#
# This middleware runs on EVERY request and automatically logs:
#   - HTTP method (GET, POST, PATCH, DELETE)
#   - Request path (/incidents, /ai/status, etc.)
#   - Response status code (200, 201, 404, 500, etc.)
#   - How long the request took to process (in milliseconds)
#
# This gives you visibility into API performance without adding
# logging code to every single route handler.
#
# Day 55: Request logging middleware

# Import time for measuring request duration
import time

# Import Starlette's BaseHTTPMiddleware — the base class for FastAPI middleware
# Starlette is the ASGI framework that FastAPI is built on top of
from starlette.middleware.base import BaseHTTPMiddleware

# Import Request type for type hints
from starlette.requests import Request

# Import our logging configuration
from app.logging_config import get_logger

# Create a logger specifically for this module
# Log messages will show "app.middleware" as the source
logger = get_logger(__name__)


# ========================================
# REQUEST LOGGING MIDDLEWARE
# ========================================

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs every HTTP request with timing information.
    
    For each request, it logs:
    - The HTTP method and path (e.g., "GET /incidents")
    - The response status code (e.g., 200, 404)
    - How long the request took in milliseconds
    
    Example log output:
    2026-04-01 14:30:45 | INFO | app.middleware | GET /incidents → 200 (12ms)
    2026-04-01 14:30:46 | INFO | app.middleware | POST /incidents → 201 (45ms)
    2026-04-01 14:30:47 | WARN | app.middleware | GET /incidents/999 → 404 (3ms)
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Called for every incoming HTTP request.
        
        Args:
            request: The incoming HTTP request object
            call_next: Function to call the actual route handler
        
        Returns:
            The response from the route handler
        """
        
        # Record the start time with high precision
        start_time = time.perf_counter()
        
        # Extract request details for logging
        # request.method is "GET", "POST", "PATCH", etc.
        method = request.method
        # request.url.path is "/incidents", "/ai/status", etc.
        path = request.url.path
        
        # Skip logging for certain paths that are too noisy
        # Health checks and OPTIONS (CORS preflight) are called constantly
        skip_paths = {"/health", "/docs", "/openapi.json", "/favicon.ico"}
        should_log = path not in skip_paths and method != "OPTIONS"
        
        try:
            # Call the actual route handler and get the response
            # This is where your route function runs (e.g., get_incidents, create_incident)
            response = await call_next(request)
            
            # Calculate how long the request took
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Log the request if it's not a skipped path
            if should_log:
                # Choose log level based on status code
                status_code = response.status_code
                
                if status_code >= 500:
                    # 5xx = server error — log as ERROR
                    logger.error(
                        "%s %s → %d (%dms)",
                        method, path, status_code, duration_ms
                    )
                elif status_code >= 400:
                    # 4xx = client error — log as WARNING
                    logger.warning(
                        "%s %s → %d (%dms)",
                        method, path, status_code, duration_ms
                    )
                else:
                    # 2xx/3xx = success — log as INFO
                    logger.info(
                        "%s %s → %d (%dms)",
                        method, path, status_code, duration_ms
                    )
            
            return response
        
        except Exception as exc:
            # If the route handler raised an unhandled exception
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "%s %s → EXCEPTION (%dms): %s",
                method, path, duration_ms, str(exc)[:100]
            )
            # Re-raise the exception so FastAPI's error handling takes over
            raise