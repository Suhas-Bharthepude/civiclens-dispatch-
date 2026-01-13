# Import APIRouter so we can define routes outside main.py
from fastapi import APIRouter


# Import List type for type hints
from typing import List 


# Import the Pydantic model that defines incident data
# .. means “go up one folder” → from routes/ to app/.
# Now Python knows schemas is inside app/.
from ..schemas.incident import IncidentCreate, IncidentRead


# Create a router object
# This groups related endpoints together 
router = APIRouter()


# Temporary in-memory storage
# This is just a Python list
# This wll be replaced by a database later
incidents_db = []


@router.post("/incidents", response_model=IncidentRead, status_code=201)
# Defines POST /incidents

def create_incident(incident: IncidentCreate):

    """
    Create a new incident.
    This simulates storing the incident before we add a real database.
    """

    
    # Generate a fake ID
    # (length of list + 1)
    incident_id = len(incidents_db) + 1

    # Create a dictionary representing the incident
    new_incident = {
        "id": incident_id,
        "description": incident.description,
        "location": incident.location,
        "source": incident.source,
        "risk_score": None,
        "transcript": None,
        "summary": None,

    }

    # Store it in memory 
    incidents_db.append(new_incident)

    # Return it to the client 
    return new_incident

@router.get("/incidents", response_model=List[IncidentRead])
def list_incidents():
    # Return all stored incidents.

    return incidents_db




