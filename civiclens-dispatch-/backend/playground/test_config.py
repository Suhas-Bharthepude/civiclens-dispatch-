# backend/playground/test_config.py
# This script tests configuration loading from .env

# Import the settings
from app.config import settings, is_development, is_production

# Print configuration (hiding passwords)
print("\n" + "="*60)
print("CIVICLENS DISPATCH - CONFIGURATION TEST")
print("="*60 + "\n")

print(f"Environment: {settings.ENVIRONMENT}")
print(f"Debug Mode: {settings.DEBUG}")
print(f"Is Development: {is_development()}")
print(f"Is Production: {is_production()}")
print(f"\nApp Title: {settings.APP_TITLE}")
print(f"Version: {settings.VERSION}")

print(f"\nDatabase User: {settings.POSTGRES_USER}")
print(f"Database Name: {settings.POSTGRES_DB}")
print(f"Database Host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")
print(f"Database URL: {settings.DATABASE_URL[:40]}... (truncated)")

print(f"\nUpload Directory: {settings.UPLOAD_DIR}")
print(f"Max Upload Size: {settings.MAX_UPLOAD_SIZE / 1024 / 1024:.1f} MB")

print(f"\nMapbox API Key: {'Set ✅' if settings.MAPBOX_API_KEY else 'Not Set ❌'}")
print(f"HuggingFace API Key: {'Set ✅' if settings.HUGGINGFACE_API_KEY else 'Not Set ❌'}")

print(f"\nSecret Key: {settings.SECRET_KEY[:10]}... (hidden)")
print(f"Token Expiration: {settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes")

print("\n" + "="*60)
print("✅ Configuration loaded successfully!")
print("="*60 + "\n")