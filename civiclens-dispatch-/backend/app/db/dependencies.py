# backend/app/db/dependencies.py
# This file provides FastAPI dependency functions for database access
# Dependencies are reusable functions injected into route handlers

# Import the async database instance
from app.db.database import database

# Import AsyncGenerator type for proper typing
from typing import AsyncGenerator

# Import databases.Database type for typing
from databases import Database


async def get_db() -> AsyncGenerator[Database, None]:
    """
    FastAPI dependency that provides a database connection.
    
    This dependency:
    1. Ensures the database is connected
    2. Yields the database instance to the route handler
    3. Keeps connection alive during request processing
    
    Usage in routes:
        @router.get("/incidents")
        async def list_incidents(db: Database = Depends(get_db)):
            # db is now available here
            query = incidents.select()
            return await db.fetch_all(query)
    
    Note: Connection lifecycle is managed in main.py startup/shutdown events,
    not here. This dependency just yields the existing connection.
    """
    # Yield the database instance
    # The route handler receives this and can use it for queries
    yield database
    
    # After the route finishes, execution returns here
    # No cleanup needed - connection persists across requests