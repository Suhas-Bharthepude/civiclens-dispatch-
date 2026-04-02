# backend/app/validators.py
# Business logic validation for incident data
#
# Pydantic handles TYPE validation (is it a string? is it a number?)
# This module handles BUSINESS validation (is the description long enough?
# is the source a valid value? is the location not just whitespace?)
#
# Usage:
#   from app.validators import validate_incident_create
#   errors = validate_incident_create(incident_data)
#   if errors:
#       raise HTTPException(status_code=400, detail=errors)
#
# Day 59: Input validation hardening

# Import List for type hints
from typing import List

# Import the Pydantic schema for type reference
from app.schemas.incident import IncidentCreate


# ========================================
# CONFIGURATION
# ========================================

# Minimum description length in characters
# Descriptions shorter than this aren't useful for dispatchers
MIN_DESCRIPTION_LENGTH = 10

# Maximum description length in characters
# Prevents abuse (someone submitting a 10MB description)
MAX_DESCRIPTION_LENGTH = 5000

# Maximum location length
MAX_LOCATION_LENGTH = 500

# Valid source values (if you want to restrict them)
# Set to None to allow any source string
VALID_SOURCES = {"citizen", "dispatcher", "sensor", "police", "fire_dept", "ems"}


# ========================================
# VALIDATION FUNCTIONS
# ========================================

def validate_incident_create(data: IncidentCreate) -> List[str]:
    """
    Validate incident creation data beyond Pydantic's type checks.
    
    Returns a list of error message strings.
    Empty list means validation passed.
    
    Args:
        data: The IncidentCreate Pydantic model (already type-validated)
    
    Returns:
        List of error messages. Empty = valid.
    
    Example:
        errors = validate_incident_create(data)
        if errors:
            raise HTTPException(status_code=400, detail={"errors": errors})
    """
    
    # Collect all validation errors (don't stop at the first one)
    errors = []
    
    # ── DESCRIPTION VALIDATION ────────────────────────
    
    # Check that description is not just whitespace
    if not data.description or not data.description.strip():
        errors.append("Description cannot be empty or just whitespace")
    else:
        # Strip whitespace for length checks
        desc = data.description.strip()
        
        # Check minimum length
        if len(desc) < MIN_DESCRIPTION_LENGTH:
            errors.append(
                f"Description must be at least {MIN_DESCRIPTION_LENGTH} characters "
                f"(got {len(desc)})"
            )
        
        # Check maximum length
        if len(desc) > MAX_DESCRIPTION_LENGTH:
            errors.append(
                f"Description must be at most {MAX_DESCRIPTION_LENGTH} characters "
                f"(got {len(desc)})"
            )
    
    # ── LOCATION VALIDATION ───────────────────────────
    
    # Location is required in our system — dispatchers need it
    if not data.location or not data.location.strip():
        errors.append("Location cannot be empty or just whitespace")
    elif len(data.location.strip()) > MAX_LOCATION_LENGTH:
        errors.append(
            f"Location must be at most {MAX_LOCATION_LENGTH} characters "
            f"(got {len(data.location.strip())})"
        )
    
    # ── SOURCE VALIDATION ─────────────────────────────
    
    # Check that source is not empty
    if not data.source or not data.source.strip():
        errors.append("Source cannot be empty or just whitespace")
    elif VALID_SOURCES and data.source.strip().lower() not in VALID_SOURCES:
        # Only validate against allowed values if VALID_SOURCES is set
        errors.append(
            f"Source must be one of: {', '.join(sorted(VALID_SOURCES))} "
            f"(got '{data.source.strip()}')"
        )
    
    return errors