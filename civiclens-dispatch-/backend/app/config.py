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
    
    # ========================================
    # ENVIRONMENT
    # ========================================
    # Current environment: development, staging, or production
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Debug mode - enables detailed error messages
    # Should be False in production for security
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    
    # ========================================
    # APPLICATION INFO
    # ========================================
    # Application title shown in API docs
    APP_TITLE: str = "CivicLens Dispatch API"
    
    # API version
    VERSION: str = "1.0.0"
    
    
    # ========================================
    # DATABASE
    # ========================================
    # Database connection URL
    # Format: postgresql+asyncpg://user:password@host:port/database
    # Falls back to SQLite if not set (for development)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )
    
    # PostgreSQL specific settings (if using PostgreSQL)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    
    # ========================================
    # FILE STORAGE
    # ========================================
    # Upload directory for media files
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "backend/app/media/tmp")
    
    # Maximum file size (in bytes) - 10MB default
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    
    
    # ========================================
    # API KEYS (Future - Days 36+)
    # ========================================
    # Mapbox API key for geocoding/maps
    MAPBOX_API_KEY: str = os.getenv("MAPBOX_API_KEY", "")
    
    # Hugging Face API key for AI models
    HUGGINGFACE_API_KEY: str = os.getenv("HUGGINGFACE_API_KEY", "")
    
    
    # ========================================
    # SECURITY (Future - Day 56)
    # ========================================
    # Secret key for JWT tokens (will add later)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # JWT token expiration (in minutes)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


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


# Helper function to check if we're in production
def is_production() -> bool:
    """
    Returns True if ENVIRONMENT is set to 'production'.
    Useful for conditional logic based on environment.
    """
    return settings.ENVIRONMENT.lower() == "production"


# Helper function to check if we're in development
def is_development() -> bool:
    """
    Returns True if ENVIRONMENT is set to 'development'.
    Useful for enabling dev-only features.
    """
    return settings.ENVIRONMENT.lower() == "development"