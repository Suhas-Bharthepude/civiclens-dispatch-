# backend/app/schemas/incident.py
# Pydantic models (schemas) for incident data validation
#
# Pydantic models define the SHAPE of data going in and out of the API.
# They automatically validate data types, required fields, and constraints.
#
# We have separate models for different operations:
#   - IncidentCreate: What the user sends when creating a new incident (input)
#   - IncidentUpdate: What the user sends when updating an incident (input)
#   - IncidentResponse: What the API sends back to the user (output)
#
# Why separate models?
#   - Create: Only needs source, description, location (user fills these in)
#   - Update: All fields optional (user might only update one field)
#   - Response: Includes ALL fields, including AI-generated ones and the ID
#
# Day 48: Added image_caption field for DETR object detection output

# Import BaseModel from Pydantic — the base class all our models inherit from
# BaseModel provides automatic data validation, serialization, and documentation
from pydantic import BaseModel, field_serializer

# Import Optional from typing — used to mark fields that can be None
# Optional[str] means the field can be a string OR None
from typing import Optional

# Import datetime for the created_at timestamp field
# This tells Pydantic to expect a datetime object (not just a string)
from datetime import datetime


# ========================================
# CREATE MODEL (Input — POST /incidents)
# ========================================

class IncidentCreate(BaseModel):
    """
    Schema for creating a new incident.
    
    This defines what data the user must provide when submitting
    a new incident report via POST /incidents.
    
    Required fields: source, description, location
    All other fields (AI-generated) are NOT included here because
    they are populated by the AI pipeline after creation.
    
    Example request body:
    {
        "source": "citizen",
        "description": "Fire reported at 123 Main Street",
        "location": "123 Main Street"
    }
    """
    
    # Who reported the incident (e.g., "citizen", "dispatcher", "sensor")
    # This is a required string field — Pydantic will reject requests without it
    source: str
    
    # Text description of what happened
    # This is the main content from the citizen's report
    # Required — every incident must have a description
    description: str
    
    # Where the incident occurred (address, intersection, or coordinates)
    # Required — dispatchers need to know where to send responders
    location: str


# ========================================
# UPDATE MODEL (Input — PATCH /incidents/{id})
# ========================================

class IncidentUpdate(BaseModel):
    """
    Schema for updating an existing incident.
    
    All fields are Optional because the user might only want to
    update one or two fields, not all of them.
    
    PATCH semantics: Only the fields included in the request body
    are updated. Fields not included are left unchanged.
    
    Example request body (updating just severity):
    {
        "severity": "high"
    }
    """
    
    # --- Core fields (user-editable) ---
    
    # Source can be updated (e.g., correcting who reported it)
    source: Optional[str] = None
    
    # Description can be updated (e.g., adding more details)
    description: Optional[str] = None
    
    # Location can be corrected
    location: Optional[str] = None
    
    # --- AI-generated fields (can be manually overridden by dispatcher) ---
    
    # Audio transcript from Whisper ASR
    transcript: Optional[str] = None
    
    # AI-generated summary from BART-Large-CNN
    summary: Optional[str] = None
    
    # Risk score (0.0 to 1.0) from BART-MNLI
    risk_score: Optional[float] = None
    
    # Incident type (fire, medical, traffic, etc.) from BART-MNLI
    incident_type: Optional[str] = None
    
    # Severity level (high, medium, low) from BART-MNLI
    severity: Optional[str] = None
    
    # Image caption from DETR object detection (Day 48)
    image_caption: Optional[str] = None


# ========================================
# RESPONSE MODEL (Output — GET /incidents, GET /incidents/{id})
# ========================================

class IncidentResponse(BaseModel):
    """
    Schema for incident data returned by the API.
    
    This includes ALL fields: the user-provided fields, the auto-generated
    fields (id, created_at), and the AI-generated fields.
    
    This model is used as the response_model in FastAPI routes,
    which means FastAPI automatically converts database rows to this
    format before sending the JSON response to the client.
    
    Example response:
    {
        "id": 1,
        "source": "citizen",
        "description": "Fire reported at 123 Main Street",
        "location": "123 Main Street",
        "created_at": "2026-03-31T21:26:00",
        "audio_path": null,
        "image_path": null,
        "transcript": "Caller reports seeing flames...",
        "summary": "Fire incident at Main Street...",
        "risk_score": 0.85,
        "incident_type": "fire",
        "severity": "high",
        "image_caption": "Objects detected: 2 cars, 1 truck"
    }
    """
    
    # --- Auto-generated fields ---
    
    # Unique ID assigned by the database (auto-incremented)
    # This is always present in responses but never in create requests
    id: int
    
    # --- Core fields (from user input) ---
    
    # Who reported the incident
    source: Optional[str] = None
    
    # Text description of what happened
    description: str
    
    # Where the incident occurred
    location: Optional[str] = None
    
    # When the incident was created in the database
    # datetime type ensures proper serialization to ISO format in JSON
    # Optional because some older records might not have this field
    created_at: Optional[datetime] = None
    
    # --- File upload paths ---
    
    # Path to the uploaded audio file on disk (if any)
    # None if no audio was uploaded with this incident
    audio_path: Optional[str] = None
    
    # Path to the uploaded image file on disk (if any)
    # None if no image was uploaded with this incident
    image_path: Optional[str] = None
    
    # --- AI-generated fields ---
    
    # Audio transcript generated by Whisper ASR (Day 34)
    # None if no audio was uploaded or transcription failed
    transcript: Optional[str] = None
    
    # AI-generated summary from BART-Large-CNN (Day 47)
    # Concise description of the incident
    summary: Optional[str] = None
    
    # Risk score from BART-MNLI zero-shot classification (Day 45)
    # Float between 0.0 (routine) and 1.0 (critical emergency)
    risk_score: Optional[float] = None
    
    # Incident type from BART-MNLI zero-shot classification (Day 46)
    # Values: "fire", "medical", "traffic", "crime", "noise", "infrastructure", "other"
    incident_type: Optional[str] = None
    
    # Severity level from BART-MNLI zero-shot classification (Day 46)
    # Values: "high", "medium", "low"
    severity: Optional[str] = None
    
    # Image caption from DETR object detection (Day 48)
    # Text description of objects detected in the uploaded image
    # Example: "Objects detected in image: 2 cars, 1 truck (3 objects total)"
    # None if no image was uploaded or analysis failed
    image_caption: Optional[str] = None
    
    # --- Pydantic configuration ---
    
    @field_serializer('created_at')
    def serialize_created_at(self, value: datetime) -> Optional[str]:
        # Append "Z" so JavaScript's new Date() treats this as UTC,
        # not local time. Without "Z", browsers interpret the string as
        # local time and display the wrong hour.
        if value is None:
            return None
        return value.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

    class Config:
        """
        Pydantic model configuration.

        from_attributes = True (formerly orm_mode = True) tells Pydantic
        to read data from SQLAlchemy model attributes, not just dictionaries.
        This allows us to pass database row objects directly to this model
        and have them automatically converted to JSON-serializable format.
        """
        from_attributes = True
IncidentRead = IncidentResponse
