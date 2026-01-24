# This file's purpose is “What API endpoints exist for incidents?”
# Its job is to answer the question "What can the client do with incidents?"




# APIRouter lets us group related API endpoints together
# HTTPException lets us return proper HTTP error responses (like 404)
# Query lets us define and validate query parameters like ?limit=10
from fastapi import APIRouter, HTTPException, Query



# List is used for type hinting response models (List[IncidentRead])
from typing import List, Optional 

# Pydantic schemas to import the request/response data models
from app.schemas.incident import IncidentCreate, IncidentRead

# Import the async database connection object
from app.db.database import database

# Import the SQLAlchemy table definition for incidents 
from app.db.models import incidents

# Router groups all endpoints for incidents
router = APIRouter()






# ------------------------------------------------------
# GET /incidents — Returns a paginated list of incidents
# ------------------------------------------------------


@router.get("/incidents", response_model=List[IncidentRead])
async def list_incidents(
    # limit controls how many incidents we return
    # default = 10
    # ge=1 means must be at least 1
    # le=100 means "must be <= 100"
    limit: int = Query(10, ge=1, le=100),

    # offset controls where we start reading from
    # default = 0 means start at the beginning
    # ge=0 means cannot be negative
    offset: int = Query(0, ge=0),


    # Optional filter: source of the incident (citizen, dispatcher, etc.)
    source: Optional[str] = Query(None),


    # Optional filter: minimum risk score
    # ge=0.0 prevents negative risk values
    min_risk_score: Optional[float] = Query(None, ge=0.0),

    # Optional sorting column 
    # We restrict allowed values manually later
    sort_by: Optional[str] = Query(None),

    # Optional sort oder
    # Default is ascending
    order: str = Query("asc"),

):





    """
    
    Returns a list of incidents with optional filtering,
    sorting, and pagination
    """


    # Start building a SELECT query from the incidents table 
    query = incidents.select()

    # ----------------------------------------
    # APPLY FILTERS (ONLY IF PROVIDED)
    # ----------------------------------------

    # If a source filter was provided
    if source is not None:
        # Add WHERE incidents.source == source
        query = query.where(incidents.c.source == source)


    # If a minimum risk score filter was provided
    if min_risk_score is not None:
        # Add WHERE incidents.risk_score >= min_risk_score
        query = query.where(incidents.c.risk_score >= min_risk_score)

    # ----------------------------------------
    # APPLY SORTING (CONTROLLED, SAFE)
    # ----------------------------------------

    # Define which columns are allowed to be sorted
    allowed_sort_columns = {
        "id": incidents.c.id,
        "risk_score": incidents.c.risk_score,
    }

    # If client requested sorting
    if sort_by is not None:
        # If the requested column is not allowed 
        if sort_by not in allowed_sort_columns:
            # Return a 400 Bad Request error
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by value. Allowed: {list(allowed_sort_columns.keys())}"
            )

        

        # Get the actual SQLAlchemy column object
        sort_column = allowed_sort_columns[sort_by]

        # Apply descending order if requested 

        if order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            # Default to ascending order
            query = query.order_by(sort_column.asc())

        

    # ----------------------------------------
    # APPLY PAGINATION (ALWAYS LAST)
    # ----------------------------------------


    # Limit how many rows are returned
    # Skip the first 'offset' rows


    query = query.limit(limit).offset(offset)




    # ----------------------------------------
    # EXECUTE QUERY
    # ----------------------------------------

    # Execute the query asynchronously 
    # fetch_all returns a list of rows
    results = await database.fetch_all(query)

    # Return the final list
    return results





# -------------------------------------------------------------
# GET /incidents/{incident_id} - Return a single incident by ID
# -------------------------------------------------------------

@router.get("/incidents/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: int):

    # Build a SELECT query that filters by incident ID
    # incidents.c.id refers to the "id" column of the table
    query = incidents.select().where(incidents.c.id == incident_id)

    # Execute the query asynchronously
    # fetch_one returns one row or None
    incident = await database.fetch_one(query)

    # If no incident was found in the database
    if incident is None:
        # Raise a 404 Not Found error
        # FastAPI converts this into an HTTP response
        raise HTTPException(status_code=404, detail="Incident not found")


    # If the incident exists, return it
    return incident




# ----------------------------------------
# POST /incidents - Create a new incident 
# ----------------------------------------

@router.post("/incidents", response_model=IncidentRead)
async def create_incident(incident: IncidentCreate):

    """
    Create a new incident and store it in the database
    """

    # Build an INSERT query for the incidents table
    # Values come from the IncidentCreate schema
    query = incidents.insert().values(
        description=incident.description,  # incident description text
        location=incident.location,        # where the incident occurred
        source=incident.source,            # who reported it
        risk_score=None,                   # AI will calculate later
        transcript=None,                   # audio transcript not generated yet
        summary=None                       # AI summary not generated yet
    )

    # Execute the INSERT query
    # This returns the ID of the newly created row
    last_record_id = await database.execute(query)

    # Return the newly created incident
    # We manually construct the response to match IncidentRead exactly
    
    return {
        **incident.dict(),
        "id": last_record_id,
        "risk_score": None,
        "transcript": None,
        "summary": None
    }






