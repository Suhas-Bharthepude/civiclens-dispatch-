<<<<<<< HEAD
from fastapi import FastAPI

# Import database tools
from app.db.database import database, engine, metadata

# Import the table so SQLAlchemy knows about it
from app.db.models import incidents

# Import the route that contains endpoints
from app.routes.incidents import router as incidents_router

# Create tables if they don't exist
# This runs once at startup
=======
# Import FastAPI class to create the API application 
from fastapi import FastAPI

# Import database tools
# database is the async database objects for queries
# engine is the SQLAlchemy sync engine for creating tables 
# metadata is for table registry 

from .db.database import database, engine, metadata

# Import the table so SQLAlchemy knows about it
# This tells SQLAlchemy about the tables defined in models.py
from app.db.models import incidents

# Import the router that contains your endpoints for incidents
from app.routes.incidents import router as incidents_router

# Create all tables if they don't exist
# This runs once at startup
# engine uses the sync driver psycopg2
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
metadata.create_all(engine)


# Create the FastAPI application
<<<<<<< HEAD
=======
# This is the main objects that runs API
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
app = FastAPI()


# Include the router
<<<<<<< HEAD
=======
# All routes in incidents_router will now be part of the app
# like POST / incidents, GET / incidents 
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
app.include_router(incidents_router)




<<<<<<< HEAD
# Startup hook: 
@app.on_event("startup")
async def startup():
    # open database connection
    await database.connect()


# Shutdown hook: 
=======
# Startup event runs when the server starts
# Connect to the async database here
@app.on_event("startup")
async def startup():
    # Connect to database if not already connected 
    await database.connect()


# Shutdown event runs when the server stops 
# Disconnect from the async database
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
@app.on_event("shutdown")
async def shutdown():
    # close database connection
    await database.disconnect()



# Root endpoint for health check
<<<<<<< HEAD
=======
# Simple GET endpoint to make sure the API is running 
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
@app.get("/")
async def root():
    return {"message": "CivicLens Dispatch API is running"}





