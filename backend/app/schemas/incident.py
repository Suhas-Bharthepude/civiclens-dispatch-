# BaseModel is the parent clas for all Pydantic models 
# BaseModel gives Validation, Type enforcement, and JSON serialization
# Field adds extra information to fields 
# Fields is used for required vs optional, examples in /docs, constraints later (length, ranges)
from pydantic import BaseModel, Field 


# The value can either exist OR be None 
from typing import Optional


# -----------------------------
# MODEL 1: Base Incident Model
# -----------------------------

""" 
This is the base model for an incident
Fields here are common to both requests (POST) and responses (GET)
"""

class IncidentBase(BaseModel):

    description: str = Field(..., example = "Fire reported in apartment building")
    # description of the incident, required (incidated by ...)

    #   description → field name
    #   : str → must be a string
    #   Field(...) → required
    #   example= → shown in /docs


    location: str = Field(..., example="123 Main St")
    # location of the incident as a string (we'll later add lat/lon)

    #   location → field name
    #   : str → must be a string
    #   Field(...) → required
    #   example= → shown in /docs
    

    source: str = Field(..., example = "citizen")
    # source of the report (citizen, dispatcher, etc..)

    #   source → field name
    #   : str → must be a string
    #   Field(...) → required
    #   example= → shown in /docs


# ------------------------------------
# MODEL 2: Incident creation (request)
# ------------------------------------


"""
Model for creating a new incident (For incoming POST requests)
Inherits all fields from IncidentBase
Additional fields can be addes if needed
"""


class IncidentCreate(IncidentBase):

    

    audio_file: Optional[str] = Field(None, example="audio123.wav")

    # Path or name of uploaded audio
    # Optional → user may not upload audio
    # Default is None
    # Safe for missing data 

    image_file: Optional[str] = Field(None, example="image123.png")

    # Path or name of uploaded image
    # Optional → user may not upload image
    # Default is None
    # Safe for missing data 

# ---------------------------------
# Model 3: Incident read (response)
# ---------------------------------

"""
Model for returning an incident in responses.
Inherits from IncidentBase and adds fields only for response
"""

class IncidentRead(IncidentBase):
    id: int # ID field that comes from database, never provided by user, and required in responses

    risk_score: Optional[float] = None
    # Score calculated by AI for prioritization 

    transcript: Optional[str] = None
    # Transcribed text from audio

    summary: Optional[str] = None
    # AI-generated summary of incident 

    # These 3 fields are optional because they don't exist immediately and they appear after async processing
     



    class Config:
<<<<<<< HEAD
        orm_mode = True
        # This tells Pydantic to read data from SQLAlchemy Object-Relational Mapping (ORM) objects
        # Allows us to return ORM models directly without converting to dictionary

=======
        from_attributes = True  # <-- v2 style (replaces orm_mode)
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)






