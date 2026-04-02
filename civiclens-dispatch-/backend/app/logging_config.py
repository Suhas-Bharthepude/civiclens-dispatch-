# backend/app/logging_config.py
# Centralized logging configuration for the entire application
#
# This replaces scattered print() statements with structured logging.
# All modules import the logger from here to ensure consistent formatting.
#
# Log levels (from least to most severe):
#   DEBUG   — Detailed diagnostic info (only in development)
#   INFO    — General operational events ("Incident created", "Pipeline started")
#   WARNING — Something unexpected but not an error ("API retrying", "Fallback used")
#   ERROR   — Something failed ("API call failed", "Database error")
#
# Day 55: Structured logging and observability

# Import Python's built-in logging module
# This is the standard way to do logging in Python — much better than print()
import logging

# Import sys to configure where log output goes
import sys


# ========================================
# CONFIGURE THE ROOT LOGGER
# ========================================

def setup_logging(level: str = "INFO"):
    """
    Configure logging for the entire application.
    
    Call this ONCE at application startup (in main.py).
    All modules that import logging.getLogger() will use this configuration.
    
    Args:
        level: Minimum log level to display. "DEBUG" shows everything,
               "INFO" shows info and above, "WARNING" shows only warnings and errors.
    """
    
    # Define the log format
    # Each log line will look like:
    # 2026-04-01 14:30:45 | INFO | app.services.asr | Transcription complete for incident 5
    log_format = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
    
    # Define the date format for timestamps
    # Example: "2026-04-01 14:30:45"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Create a handler that writes to stdout (terminal)
    # StreamHandler(sys.stdout) sends logs to the terminal
    handler = logging.StreamHandler(sys.stdout)
    
    # Set the format on the handler
    # Formatter turns the log record into the string we defined above
    handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    
    # Get the root logger — this is the parent of ALL loggers in the application
    root_logger = logging.getLogger()
    
    # Set the minimum log level
    # Convert string like "INFO" to the logging constant like logging.INFO
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Remove any existing handlers to avoid duplicate log lines
    # This can happen if setup_logging is called more than once (e.g., in tests)
    root_logger.handlers.clear()
    
    # Add our configured handler
    root_logger.addHandler(handler)
    
    # Quiet down noisy third-party libraries
    # These libraries log a LOT of debug info that clutters our output
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log that logging is configured (meta!)
    root_logger.info("Logging configured at %s level", level)


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger for a specific module.
    
    Usage in any module:
        from app.logging_config import get_logger
        logger = get_logger(__name__)
        logger.info("Something happened")
    
    The __name__ parameter automatically uses the module's dotted path
    (e.g., "app.services.asr") so you can see WHERE each log came from.
    
    Args:
        name: Usually __name__ — the module's Python path
    
    Returns:
        A configured Logger instance
    """
    return logging.getLogger(name)