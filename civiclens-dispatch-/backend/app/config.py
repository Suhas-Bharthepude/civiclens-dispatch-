# backend/app/config.py
# This file manages all configuration settings for the application
# It reads from environment variables (.env file) to keep secrets safe

# Import os to access environment variables
import os

# Import load_dotenv to read .env file automatically
from dotenv import load_dotenv

# Load environment variables from .env file
# This must happen before accessing os.getenv()
load_dotenv()


class Settings:
    """
    Application configuration settings.
    All values are loaded from environment variables.
    """
    
    # Database connection URL
    # Format: postgresql+asyncpg://user:password@host:port/database
    # Falls back to SQLite if not set (for development)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )
    
    # Debug mode - enables detailed error messages
    # Should be False in production
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Application title
    APP_TITLE: str = "CivicLens Dispatch API"
    
    # API version
    VERSION: str = "1.0.0"
    
    # Upload directory for media files
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/app/media/tmp")
    
    # PostgreSQL specific settings (if using PostgreSQL)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")


# Create a single settings instance to use throughout the app
settings = Settings()


# Helper function to build PostgreSQL URL from individual components
def get_postgres_url() -> str:
    """
    Constructs PostgreSQL connection URL from environment variables.
    Only use this if you want to override DATABASE_URL.
    """
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )