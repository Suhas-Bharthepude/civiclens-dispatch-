# backend/app/db/database.py
# This file sets up the database connection for the application
# It uses async database access for FastAPI

# Import SQLAlchemy's create_engine for sync operations (table creation only)
from sqlalchemy import create_engine

# Import Database class for async operations
from databases import Database

# Import settings from config
from app.config import settings

# Import the canonical metadata that has the incidents table registered on it.
# This MUST come from models.py — database.py must not create its own MetaData()
# because create_all(engine) would then run on an empty registry and create nothing.
from app.db.models import metadata


# Create the async database connection object
# This will be used for all CRUD operations in routes
database = Database(settings.DATABASE_URL)


# Create a sync engine for table creation
# We need this because create_all() is a sync operation
# For SQLite: remove +aiosqlite for sync engine
if "sqlite" in settings.DATABASE_URL:
    # Use plain sqlite:/// for sync engine (table creation)
    sync_db_url = settings.DATABASE_URL.replace("+aiosqlite", "")
    engine = create_engine(
        sync_db_url,
        connect_args={"check_same_thread": False}
    )
else:
    # For PostgreSQL: replace asyncpg with psycopg2 for sync engine
    sync_db_url = settings.DATABASE_URL.replace(
        "postgresql+asyncpg://",
        "postgresql+psycopg2://"
    )
    engine = create_engine(sync_db_url)
