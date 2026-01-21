from fastapi import FastAPI

# Import database tools
from app.db.database import database, engine, metadata

# Import the table so SQLAlchemy knows about it
from app.db.models import incidents

# Import the route that contains endpoints
from app.routes.incidents import router as incidents_router

# Create tables if they don't exist
# This runs once at startup
metadata.create_all(engine)


# Create the FastAPI application
app = FastAPI()


# Include the router
app.include_router(incidents_router)




# Startup hook: 
@app.on_event("startup")
async def startup():
    # open database connection
    await database.connect()


# Shutdown hook: 
@app.on_event("shutdown")
async def shutdown():
    # close database connection
    await database.disconnect()



# Root endpoint for health check
@app.get("/")
async def root():
    return {"message": "CivicLens Dispatch API is running"}





