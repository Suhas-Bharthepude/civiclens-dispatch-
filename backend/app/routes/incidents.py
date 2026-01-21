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


