# backend/app/config.py
# Centralized configuration management for the entire application
#
# All settings are loaded from environment variables (via .env file).
# Default values are provided for development — override them in
# production by setting the corresponding environment variable.
#
# Usage in any module:
#   from app.config import settings
#   print(settings.DATABASE_URL)
#   print(settings.DEBUG)
#
# Day 57: Enhanced with production-ready defaults and documentation
# Day 67: Added environment-aware properties (effective_debug, effective_cors_origins, etc.)
#         and configure_logging / print_startup_summary helpers

# Import os to read environment variables
import os
import logging

# Import load_dotenv to load variables from the .env file
# The .env file is read once when this module is first imported
from dotenv import load_dotenv

# Load the .env file into the environment
# This makes variables in .env accessible via os.getenv()
# The .env file is NOT committed to git (it's in .gitignore)
load_dotenv()


# ========================================
# SETTINGS CLASS
# ========================================

class Settings:
    """
    Application settings loaded from environment variables.

    Each setting has a default value suitable for local development.
    In production, override via environment variables or .env file.

    Example .env file:
        DEBUG=false
        DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
        HUGGINGFACE_API_KEY=hf_abc123...
        CORS_ORIGINS=https://myapp.example.com
    """

    # ── APPLICATION ─────────────────────────────────

    # Application title — shown in API docs and health check
    APP_TITLE: str = os.getenv("APP_TITLE", "CivicLens Dispatch API")

    # Application version — shown in API docs and health check
    VERSION: str = os.getenv("VERSION", "1.0.0")

    # Debug mode — enables detailed error messages and auto-reload
    # In production, set to "false" to hide internal error details
    # os.getenv returns a string, so we compare to "true"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Environment name — "development", "staging", or "production"
    # Used for conditional logic (e.g., different logging levels)
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")

    # ── DATABASE ────────────────────────────────────

    # Async database URL used by the 'databases' library for queries
    # Default: SQLite file in the current directory (development)
    # Production: PostgreSQL URL like postgresql+asyncpg://user:pass@host/dbname
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./civiclens.db"
    )

    # Sync database URL used by SQLAlchemy for table creation
    # This is derived from DATABASE_URL by removing the async driver
    # SQLAlchemy's create_all() requires a synchronous engine
    @property
    def SYNC_DATABASE_URL(self) -> str:
        """Convert async database URL to sync URL for table creation."""
        url = self.DATABASE_URL
        # Replace async drivers with sync equivalents
        if "aiosqlite" in url:
            return url.replace("sqlite+aiosqlite", "sqlite")
        if "asyncpg" in url:
            return url.replace("postgresql+asyncpg", "postgresql")
        return url

    # ── AUTH (Day 72) ────────────────────────────────

    # Secret key used to sign JWTs.
    # NEVER commit a real secret — this default is intentionally obvious
    # so it cannot be shipped to production without a visible change.
    # Generate a production value with: openssl rand -hex 32
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE-ME-dev-only-not-for-production")

    # ── AI / HUGGING FACE ───────────────────────────

    # Hugging Face API key for accessing AI models
    # Get yours at: https://huggingface.co/settings/tokens
    # NEVER commit this value — always load from environment
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")

    # Whether to use mock AI services instead of real API calls
    # Set to "true" for testing without consuming API quota
    USE_MOCK_AI: bool = os.getenv("USE_MOCK_AI", "false").lower() == "true"

    # ── CORS (Cross-Origin Resource Sharing) ────────

    # Comma-separated list of allowed frontend origins
    # Default "*" allows any origin (fine for development)
    # Production: set to your actual frontend URL, e.g., "https://myapp.com"
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")

    @property
    def cors_origin_list(self) -> list:
        """Parse CORS_ORIGINS string into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        # Split comma-separated origins into a list
        # "https://app.com,https://admin.com" → ["https://app.com", "https://admin.com"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # ── FILE UPLOADS ────────────────────────────────

    # Base directory for uploaded media files
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/app/media/tmp")

    # Maximum file size for uploads (in bytes)
    # Default: 10 MB
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(10 * 1024 * 1024)))

    # ── LOGGING ─────────────────────────────────────

    # Minimum log level: DEBUG, INFO, WARNING, ERROR
    # Development: INFO shows useful operational data
    # Production: WARNING reduces noise
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # ── ENVIRONMENT-AWARE PROPERTIES (Day 67) ───────

    @property
    def is_development(self) -> bool:
        """True when running locally in development mode."""
        return self.ENVIRONMENT == "development"

    @property
    def effective_debug(self) -> bool:
        """
        Debug is always forced off in production regardless of the DEBUG flag.
        This prevents accidental debug mode in a live environment.
        """
        if not self.is_development:
            return False
        return self.DEBUG

    @property
    def effective_cors_origins(self) -> list:
        """
        In development, allow all origins so the local React dev server can connect.
        In production, restrict to the explicitly configured frontend URL(s).
        """
        if self.is_development:
            return ["*"]
        return self.cors_origin_list

    @property
    def effective_log_level(self) -> str:
        """
        In production, bump the floor to WARNING to reduce noise.
        In development, respect whatever LOG_LEVEL is set to.
        """
        if not self.is_development:
            return "WARNING"
        return self.LOG_LEVEL


# ========================================
# CREATE SINGLETON INSTANCE
# ========================================

# Create one Settings instance that the entire app shares
# Import this in any module: from app.config import settings
settings = Settings()


# ========================================
# LOGGING HELPERS (Day 67)
# ========================================

def configure_logging() -> None:
    """
    Configure Python's root logger based on the current environment.

    Development: DEBUG level — verbose output to help during development
    Production:  WARNING level — only log problems

    Call this once at startup before any log messages are emitted.
    """
    level = getattr(logging, settings.effective_log_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def print_startup_summary() -> None:
    """
    Print a human-readable configuration summary to the terminal.
    Only runs in development — silently skipped in production.
    """
    if not settings.is_development:
        return

    db_display = (
        settings.DATABASE_URL.split("@")[-1]
        if "@" in settings.DATABASE_URL
        else settings.DATABASE_URL
    )

    print("\n" + "=" * 50)
    print(f"  {settings.APP_TITLE} v{settings.VERSION}")
    print(f"  Environment : {settings.ENVIRONMENT}")
    print(f"  Debug       : {settings.effective_debug}")
    print(f"  Log level   : {settings.effective_log_level}")
    print(f"  Database    : {db_display}")
    print(f"  CORS origins: {settings.effective_cors_origins}")
    print(f"  Mock AI     : {settings.USE_MOCK_AI}")
    print("=" * 50 + "\n")
