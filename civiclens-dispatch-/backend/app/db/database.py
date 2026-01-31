# backend/app/db/database.py
# This file sets up the database connection for the application
# It uses async database access for FastAPI

# Import SQLAlchemy's MetaData to track table definitions
from sqlalchemy import MetaData

# Import SQLAlchemy's create_engine for sync operations (table creation only)
from sqlalchemy import create_engine

# Import Database class for async operations
from databases import Database

# Import settings from config
from app.config import settings


# Create the async database connection object
# This will be used for all CRUD operations in routes
database = Database(settings.DATABASE_URL)


# Create a sync engine for table creation
# We need this because create_all() is a sync operation
# connect_args only needed for SQLite
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL, no special connect_args needed
    # But we need to use psycopg2 (sync) for create_all
    # Replace asyncpg with psycopg2 for the sync engine
    sync_db_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql+psycopg2://"
    )
    engine = create_engine(sync_db_url)


# Shared metadata object
# All table definitions will register here
metadata = MetaData()