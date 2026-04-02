# backend/app/error_handlers.py
# Global exception handlers for the FastAPI application
#
# These catch unhandled exceptions and return clean JSON responses
# instead of raw Python tracebacks.
#
# In development: full error details in response + logged to console
# In production: generic message in response + full details logged internally
#
# Day 59: Error handling hardening

# Import FastAPI's Request and JSONResponse for building error responses
from fastapi import Request
from fastapi.responses import JSONResponse

# Import FastAPI's built-in exception types
from fastapi.exceptions import RequestValidationError

# Import Starlette's HTTP exception (FastAPI builds on Starlette)
from starlette.exceptions import HTTPException as StarletteHTTPException

# Import our logging and config
from app.logging_config import get_logger
from app.config import settings

# Create a logger for this module
logger = get_logger(__name__)


# ========================================
# REGISTER ALL EXCEPTION HANDLERS
# ========================================

def register_exception_handlers(app):
    """
    Register all custom exception handlers with the FastAPI app.
    
    Call this once in main.py after creating the app:
        register_exception_handlers(app)
    
    Args:
        app: The FastAPI application instance
    """
    
    # ── HANDLER 1: HTTP Exceptions (404, 403, etc.) ────
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Handle HTTP exceptions (404 Not Found, 403 Forbidden, etc.)
        These are intentional errors raised by our code with raise HTTPException(...)
        """
        # Log the error
        logger.warning(
            "HTTP %d on %s %s: %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail
        )
        
        # Return a clean JSON response
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "status_code": exc.status_code,
                "message": exc.detail,
                "path": request.url.path,
            }
        )
    
    # ── HANDLER 2: Validation Errors (bad request body) ─
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Handle Pydantic validation errors.
        These occur when the request body doesn't match the expected schema.
        Example: missing required field, wrong data type, etc.
        """
        # Extract the validation error details
        # Pydantic provides detailed info about what went wrong
        errors = exc.errors()
        
        # Build a list of human-readable error messages
        error_messages = []
        for error in errors:
            # error["loc"] is the location of the bad field, e.g., ("body", "description")
            # error["msg"] is the error message, e.g., "field required"
            field = " → ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        logger.warning(
            "Validation error on %s %s: %s",
            request.method,
            request.url.path,
            "; ".join(error_messages)
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": True,
                "status_code": 422,
                "message": "Validation error — check your request data",
                "details": error_messages,
                "path": request.url.path,
            }
        )
    
    # ── HANDLER 3: Unhandled Exceptions (500 errors) ────
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Catch-all handler for any unhandled exception.
        This prevents raw Python tracebacks from reaching the user.
        
        In development: includes the error type and message in the response
        In production: returns a generic message (doesn't expose internals)
        """
        # Always log the full error internally
        logger.error(
            "Unhandled exception on %s %s: %s: %s",
            request.method,
            request.url.path,
            type(exc).__name__,
            str(exc),
            exc_info=True  # Include the full traceback in the log
        )
        
        # Build the response based on environment
        if settings.DEBUG:
            # Development: show the error details to help debugging
            content = {
                "error": True,
                "status_code": 500,
                "message": "Internal server error",
                "debug_info": {
                    "exception_type": type(exc).__name__,
                    "exception_message": str(exc)[:500],
                },
                "path": request.url.path,
            }
        else:
            # Production: generic message — don't expose internals
            content = {
                "error": True,
                "status_code": 500,
                "message": "An unexpected error occurred. Please try again later.",
                "path": request.url.path,
            }
        
        return JSONResponse(
            status_code=500,
            content=content
        )