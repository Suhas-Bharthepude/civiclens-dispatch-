<<<<<<< HEAD
# This file's purpose is “What API endpoints exist for incidents?”

# FastAPI router lets us group related endpoints
from fastapi import APIRouter


from typing import List

# Pydantic schemas
from app.schemas.incident import IncidentCreate, IncidentRead

# Database connection
from app.db.database import database

# SQLAlchemy table definition
from app.db.models import incidents



# Router groups all endpoints for incidents
router = APIRouter()


# ------------------------------
# Create incident
# ------------------------------

@router.post("/incidents", response_model=IncidentRead)
async def create_incident(incident: IncidentCreate):
    """
    Create a new incident in the database.
    This is now async and persistent
    """

    # Build an INSERT query
    query = incidents.insert().values(
        description=incident.description,
        location=incident.location,
        source=incident.source,
        risk_score=None,
        transcript=None,
        summary=None
    )

    last_record_id = await database.execute(query)

    # Return the created incident
    return {**incident.dict(), "id": last_record_id, "risk_score": None, "transcript": None, "summary": None}





# ------------------------------
# List all incidents
# ------------------------------
@router.get("/incidents", response_model=List[IncidentRead])
async def list_incidents():
    """
    List all incidents from the database asynchronously.
    """
    query = incidents.select()
    all_incidents = await database.fetch_all(query)
    return all_incidents


=======
# Import FastAPI tools for creating routes, handling dependencies, and raising errors
from fastapi import APIRouter, Depends, HTTPException

# Import a function that provides a database connection (not used directly here but common in FastAPI apps)
from app.db.dependencies import get_db

# Import the database object used to run queries asynchronously
from app.db.database import database

# Import the "incidents" table model so we can build SQL queries against it
from app.db.models import incidents

# Import Pydantic schemas that define what data we accept (IncidentCreate)
# and what data we return (IncidentRead)
from app.schemas.incident import IncidentCreate, IncidentRead

# Create a router object that will hold all the endpoints for incidents
router = APIRouter()

# -----------------------------
# GET all incidents
# -----------------------------

# Define a GET endpoint at /incidents that returns a list of IncidentRead objects
@router.get("/incidents", response_model=list[IncidentRead])
async def read_incidents():
    # Build a SQL query that selects all rows from the incidents table
    query = incidents.select()
    # Execute the query and fetch all results from the database
    results = await database.fetch_all(query)
    # Return the list of incidents to the client
    return results

# -----------------------------
# GET a single incident by ID
# -----------------------------

# Define a GET endpoint that takes an incident_id and returns one IncidentRead object
@router.get("/incidents/{incident_id}", response_model=IncidentRead)
async def read_incident(incident_id: int):
    # Build a SQL query that selects the row where the id matches the given incident_id
    query = incidents.select().where(incidents.c.id == incident_id)
    # Fetch exactly one row from the database
    incident = await database.fetch_one(query)
    # If no row was found, raise a 404 error so the client knows it doesn't exist
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    # Return the incident data
    return incident

# -----------------------------
# POST a new incident
# -----------------------------

# Define a POST endpoint that accepts an IncidentCreate object and returns the created row
@router.post("/incidents", response_model=IncidentRead)
async def create_incident(incident: IncidentCreate):
    # Build an INSERT query with values taken from the incoming request body
    # The title is auto-generated from the description (first 50 chars + "..." if too long)
    query = incidents.insert().values(
        title=incident.description[:50] + "..." if len(incident.description) > 50 else incident.description,
        description=incident.description,
        location=incident.location,
        source=incident.source,
        risk_score=None,   # Set to None for now (can be updated later)
        transcript=None,   # Also set to None
        summary=None       # Also set to None
    )

    # Execute the INSERT query and get the ID of the newly created row
    last_record_id = await database.execute(query)

    # Build a SELECT query to fetch the full row we just inserted
    query = incidents.select().where(incidents.c.id == last_record_id)

    # Fetch the newly created incident from the database
    new_incident = await database.fetch_one(query)

    # Return the full incident data to the client
    return new_incident
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
