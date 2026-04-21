# backend/app/routes/incidents.py
#
# FastAPI route handlers for /incidents endpoints.
#
# Route order (IMPORTANT — specific before parameterized):
#   POST   /incidents              → create_incident
#   GET    /incidents              → list_incidents (with search, filter, sort)
#   GET    /incidents/stats        → get_incident_stats
#   GET    /incidents/{id}         → get_incident
#   PATCH  /incidents/{id}         → update_incident
#   DELETE /incidents/{id}         → delete_incident
#   POST   /incidents/{id}/audio   → upload_audio
#   POST   /incidents/{id}/image   → upload_image
#   POST   /incidents/{id}/reprocess → reprocess_incident
#
# Day 44: Added search query parameter
# Day 56: Added sort_by and sort_dir query parameters
# Day 59: Added business validation on create
# Day 60: Fixed double sorting, fixed stats endpoint

# Import FastAPI components used across multiple endpoints
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks

# Import SQLAlchemy functions for building queries
# func: aggregate functions like COUNT, AVG
# select: build SELECT queries
# case: SQL CASE WHEN expressions (used in stats)
# or_: combine WHERE conditions with OR (used in search)
from sqlalchemy import func, select, case, or_

# Import datetime for setting created_at timestamps
from datetime import datetime, timezone

# Import database connection for executing queries
from app.db.database import database

# Import incidents table definition for building SQL queries
from app.db.models import incidents

# Import Pydantic schemas for request/response validation
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentRead

# Import the AI pipeline processor (runs in background after create/upload)
from app.services.incident_processor import process_incident

# Import file upload utility
from app.utils.file_utils import save_upload_file

# Import business logic validators (Day 59)
from app.validators import validate_incident_create

# Import uuid (used by file upload utility)
import uuid


# ========================================
# ROUTER SETUP
# ========================================

# Create a router with /incidents prefix
# All endpoints in this file start with /incidents
router = APIRouter(prefix="/incidents", tags=["incidents"])


# ============================================================
# POST /incidents — Create a new incident
# ============================================================

@router.post("", response_model=IncidentRead, status_code=201)
async def create_incident(
    incident_data: IncidentCreate,
    background_tasks: BackgroundTasks,
):
    """
    Create a new incident and trigger AI processing in the background.
    
    The incident is created immediately with core fields.
    AI fields (transcript, summary, type, severity, risk_score) start as None
    and are filled in by the background AI pipeline.
    """

    # ── BUSINESS VALIDATION (Day 59) ──────────────────
    # Pydantic already checked types (is source a string?)
    # Now check business rules (is description long enough? is source valid?)
    validation_errors = validate_incident_create(incident_data)
    if validation_errors:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation_errors}
        )

    # Build INSERT query with all initial fields
    # AI fields start as None — the background pipeline fills them in
    insert_query = incidents.insert().values(
        description=incident_data.description,
        source=incident_data.source,
        location=incident_data.location,
        # Set created_at to current UTC time
        created_at=datetime.now(timezone.utc),
        # All AI fields start as None
        transcript=None,
        summary=None,
        risk_score=None,
        incident_type=None,
        severity=None,
        audio_path=None,
        image_path=None,
        # New incidents start as pending — dispatcher changes via status buttons
        status="pending",
    )

    # Execute the INSERT and get the auto-generated ID
    new_id = await database.execute(insert_query)

    # Fetch the complete new incident to return in the response
    select_query = incidents.select().where(incidents.c.id == new_id)
    new_incident = await database.fetch_one(select_query)

    # Schedule AI processing to run in the background
    # This returns immediately — AI processing happens asynchronously
    background_tasks.add_task(
        process_incident,
        new_id,
        "New incident created"
    )

    # Return the created incident as a dict
    return dict(new_incident)


# ============================================================
# GET /incidents — List incidents with optional filters + search + sort
# ============================================================

@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    # Optional filter: show only incidents of this type
    incident_type: str = None,
    # Optional filter: show only incidents with this severity
    severity: str = None,
    # Optional search: full-text search across multiple fields (Day 44)
    search: str = None,
    # Sort column: which field to sort by (Day 56)
    sort_by: str = "created_at",
    # Sort direction: "asc" or "desc" (Day 56)
    sort_dir: str = "desc",
):
    """
    Fetch all incidents with optional filtering, searching, and sorting.

    Query parameters:
      ?incident_type=fire        — filter by type
      ?severity=high             — filter by severity
      ?search=oak+street         — search across description, location, transcript, summary
      ?sort_by=risk_score        — sort by column (created_at, risk_score, severity, incident_type, id)
      ?sort_dir=desc             — sort direction (asc or desc)

    Filters can be combined: ?incident_type=fire&search=oak+street&sort_by=risk_score
    """

    # Start with a basic SELECT * FROM incidents
    query = incidents.select()

    # ── APPLY EXACT-MATCH FILTERS ─────────────────────
    if incident_type:
        query = query.where(incidents.c.incident_type == incident_type)
    if severity:
        query = query.where(incidents.c.severity == severity)

    # ── APPLY SEARCH (Day 44) ─────────────────────────
    # If a search term was provided, check multiple columns using OR
    if search and search.strip():
        # Strip whitespace from both ends
        search_term = search.strip()

        # Build the LIKE pattern with wildcards
        # "%fire%" matches "fire", "Fire reported", "big fire nearby", etc.
        like_pattern = f"%{search_term}%"

        # ilike() is case-insensitive LIKE — "Fire" matches "%fire%"
        # or_() combines conditions with SQL OR
        search_condition = or_(
            incidents.c.description.ilike(like_pattern),
            incidents.c.location.ilike(like_pattern),
            incidents.c.transcript.ilike(like_pattern),
            incidents.c.summary.ilike(like_pattern),
        )

        # Add search condition to the query
        query = query.where(search_condition)

    # ── APPLY SORTING (Day 56) ────────────────────────
    # Whitelist of allowed sort columns to prevent SQL injection
    # Only these column names can be used — any other value defaults to created_at
    allowed_sort_columns = {
        "created_at": incidents.c.created_at,
        "risk_score": incidents.c.risk_score,
        "severity": incidents.c.severity,
        "incident_type": incidents.c.incident_type,
        "id": incidents.c.id,
    }

    # Get the sort column from the whitelist (default to created_at)
    sort_column = allowed_sort_columns.get(sort_by, incidents.c.created_at)

    # Apply sort direction
    if sort_dir.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    # Execute the query and fetch all matching rows
    rows = await database.fetch_all(query)

    # Convert each database row to a dict for JSON serialization
    return [dict(row) for row in rows]


# ============================================================
# GET /incidents/stats — Aggregate statistics
# ============================================================
# MUST be defined before /{incident_id} to prevent "stats" matching as an ID
#
# Day 60: Fixed — removed references to non-existent 'status' column

@router.get("/stats")
async def get_incident_stats():
    """
    Return aggregate counts of all incidents.
    Used by the StatsBar component for dashboard KPIs.
    """

    stats_query = select(
        # Total count of all incidents
        func.count().label("total"),
        # Counts by severity level
        func.count(case((incidents.c.severity == "critical", 1))).label("critical_count"),
        func.count(case((incidents.c.severity == "high", 1))).label("high_count"),
        func.count(case((incidents.c.severity == "medium", 1))).label("medium_count"),
        func.count(case((incidents.c.severity == "low", 1))).label("low_count"),
        # Counts by incident type
        func.count(case((incidents.c.incident_type == "fire", 1))).label("fire_count"),
        func.count(case((incidents.c.incident_type == "medical", 1))).label("medical_count"),
        func.count(case((incidents.c.incident_type == "crime", 1))).label("crime_count"),
        func.count(case((incidents.c.incident_type == "traffic", 1))).label("traffic_count"),
        func.count(case((incidents.c.incident_type == "noise", 1))).label("noise_count"),
        func.count(case((incidents.c.incident_type == "infrastructure", 1))).label("infrastructure_count"),
        func.count(case((incidents.c.incident_type == "other", 1))).label("other_count"),
        # Count of high-risk incidents (risk score above 0.7)
        func.count(case((incidents.c.risk_score > 0.7, 1))).label("high_risk_count"),
        # Count of incidents with audio files attached
        func.count(case((incidents.c.audio_path != None, 1))).label("with_audio_count"),
        # Count of incidents that have been AI-processed (have a summary)
        func.count(case((incidents.c.summary != None, 1))).label("ai_processed_count"),
    ).select_from(incidents)

    row = await database.fetch_one(stats_query)
    raw = dict(row)

    return {
        "total": raw["total"],
        "by_severity": {
            "critical": raw["critical_count"],
            "high":     raw["high_count"],
            "medium":   raw["medium_count"],
            "low":      raw["low_count"],
        },
        "by_type": {
            "fire":           raw["fire_count"],
            "medical":        raw["medical_count"],
            "crime":          raw["crime_count"],
            "traffic":        raw["traffic_count"],
            "noise":          raw["noise_count"],
            "infrastructure": raw["infrastructure_count"],
            "other":          raw["other_count"],
        },
        "high_risk_count":    raw["high_risk_count"],
        "with_audio_count":   raw["with_audio_count"],
        "ai_processed_count": raw["ai_processed_count"],
    }


# ============================================================
# GET /incidents/{id} — Get single incident
# ============================================================
# Defined AFTER /stats to prevent "stats" matching as an ID

@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: int):
    """Fetch a single incident by ID."""
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return dict(incident)


# ============================================================
# PATCH /incidents/{id} — Update an incident
# ============================================================

@router.patch("/{incident_id}", response_model=IncidentRead)
async def update_incident(incident_id: int, update_data: IncidentUpdate):
    """Partially update an incident (used for status changes, manual overrides)."""

    # Check if incident exists
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # exclude_unset=True means only include fields the client actually sent
    # This prevents accidentally overwriting fields with None
    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    # Execute the UPDATE query
    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(**update_fields)
    )
    await database.execute(update_query)

    # Fetch and return the updated incident
    updated = await database.fetch_one(check_query)
    return dict(updated)


# ============================================================
# DELETE /incidents/{id}
# ============================================================

@router.delete("/{incident_id}", status_code=204)
async def delete_incident(incident_id: int):
    """Permanently delete an incident."""
    # Check if incident exists
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Execute the DELETE query
    delete_query = incidents.delete().where(incidents.c.id == incident_id)
    await database.execute(delete_query)
    return None


# ============================================================
# POST /incidents/{id}/audio — Upload audio file
# ============================================================

@router.post("/{incident_id}/audio")
async def upload_audio(
    incident_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload an audio file and re-trigger AI processing."""

    # Check if incident exists
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Validate file type
    allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", "audio/x-m4a"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")

    # Save the file to disk with a unique name
    file_path = await save_upload_file(file, subfolder="audio")

    # Update the incident with the audio file path
    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(audio_path=file_path)
    )
    await database.execute(update_query)

    # Re-trigger AI pipeline (now includes audio transcription)
    background_tasks.add_task(process_incident, incident_id, "Audio uploaded — re-processing")

    return {"message": "Audio uploaded successfully", "file_path": file_path, "incident_id": incident_id}


# ============================================================
# POST /incidents/{id}/image — Upload image file
# ============================================================

@router.post("/{incident_id}/image")
async def upload_image(
    incident_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """Upload an image file and re-trigger AI processing."""

    # Check if incident exists
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/heif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")

    # Save the file to disk with a unique name
    file_path = await save_upload_file(file, subfolder="images")

    # Update the incident with the image file path
    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(image_path=file_path)
    )
    await database.execute(update_query)

    # Re-trigger AI pipeline (now includes image analysis)
    background_tasks.add_task(process_incident, incident_id, "Image uploaded — re-processing")

    return {"message": "Image uploaded successfully", "file_path": file_path, "incident_id": incident_id}


# ============================================================
# POST /incidents/{id}/reprocess — Re-run AI pipeline
# ============================================================

@router.post("/{incident_id}/reprocess")
async def reprocess_incident(
    incident_id: int,
    background_tasks: BackgroundTasks,
):
    """
    Re-run the full AI pipeline on an existing incident.

    Use this when:
    - Original AI processing failed (timeout, rate limit, model down)
    - Incident was updated and needs re-analysis
    - AI models have been improved and you want fresh results

    The AI pipeline runs in the background — endpoint returns immediately.
    """

    # Check if incident exists
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)
    if not incident:
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )

    # Queue the AI pipeline to run in the background
    background_tasks.add_task(
        process_incident,
        incident_id,
        f"Reprocessing incident {incident_id} (manual trigger)"
    )

    # Return confirmation immediately
    return {
        "message": f"Reprocessing queued for incident {incident_id}",
        "incident_id": incident_id,
        "status": "queued",
        "note": "AI pipeline will run in the background. Refresh to see updated results."
    }