# backend/app/routes/incidents.py
#
# FastAPI route handlers for the /incidents endpoints.
# Each function here handles one HTTP request type + URL combination.
#
# Day 41 addition: GET /incidents/stats
# Returns aggregate counts of all incidents in the database.
#
# IMPORTANT: The /stats route is defined BEFORE the /{id} route.
# If /{id} came first, FastAPI would treat "stats" as an incident ID
# and return a 404/422 error instead of the stats response.
#
# Existing routes (unchanged):
#   POST   /incidents          → create_incident()
#   GET    /incidents          → list_incidents()
#   GET    /incidents/stats    → get_incident_stats()  ← NEW DAY 41
#   GET    /incidents/{id}     → get_incident()
#   PATCH  /incidents/{id}     → update_incident()
#   DELETE /incidents/{id}     → delete_incident()
#   POST   /incidents/{id}/audio → upload_audio()
#   POST   /incidents/{id}/image → upload_image()

# FastAPI imports for routing, file uploads, background tasks, and HTTP errors
from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks

# sqlalchemy provides functions for building complex SQL queries
# func gives us SQL aggregate functions like COUNT() and SUM()
from sqlalchemy import func, select, case

# Our async database connection (connects to SQLite in dev, PostgreSQL in prod)
from app.db.database import database

# The SQLAlchemy table definition — used to build queries
from app.db.models import incidents

# Pydantic schemas for request/response validation
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentRead

# The background AI processing pipeline that runs after each new incident
from app.services.incident_processor import process_incident

# File utility functions for saving uploads to disk
from app.utils.file_utils import save_upload_file

# Python's uuid module for generating unique filenames
import uuid

# APIRouter creates a group of related routes
# prefix="/incidents" means all routes here start with /incidents
router = APIRouter(prefix="/incidents", tags=["incidents"])


# ============================================================
# POST /incidents — Create a new incident
# ============================================================
# This route has not changed — shown here for context/ordering

@router.post("", response_model=IncidentRead, status_code=201)
async def create_incident(
    incident_data: IncidentCreate,
    background_tasks: BackgroundTasks,
):
    """
    Create a new incident report and trigger AI processing in the background.

    The AI pipeline (transcription, classification, summarization) runs
    asynchronously — the response returns immediately with the new incident ID.
    """

    # Build the INSERT query using SQLAlchemy
    # .values() sets the initial field values from the request body
    insert_query = incidents.insert().values(
        description=incident_data.description,
        source=incident_data.source,
        location=incident_data.location,
        status="pending",       # All new incidents start as pending
        transcript=None,        # Will be filled by AI pipeline
        summary=None,           # Will be filled by AI pipeline
        risk_score=None,        # Will be filled by AI pipeline
        incident_type=None,     # Will be filled by AI pipeline
        severity=None,          # Will be filled by AI pipeline
        audio_path=None,        # Will be set when audio is uploaded
        image_path=None,        # Will be set when image is uploaded
    )

    # Execute the INSERT and get the new row's ID
    new_id = await database.execute(insert_query)

    # Fetch the complete newly-created incident to return in the response
    select_query = incidents.select().where(incidents.c.id == new_id)
    new_incident = await database.fetch_one(select_query)

    # Schedule the AI pipeline to run in the background
    # background_tasks.add_task() runs after this function returns the response
    # This means the API responds instantly — the AI processing happens separately
    background_tasks.add_task(
        process_incident,
        new_id,
        "New incident created"
    )

    return dict(new_incident)


# ============================================================
# GET /incidents — List all incidents with optional filters
# ============================================================

@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    status: str = None,
    incident_type: str = None,
    severity: str = None,
):
    """
    Fetch all incidents from the database.
    Optional query parameters filter the results.
    """

    # Start with a basic SELECT * FROM incidents
    query = incidents.select()

    # Apply filters if provided as query parameters
    if status:
        query = query.where(incidents.c.status == status)
    if incident_type:
        query = query.where(incidents.c.incident_type == incident_type)
    if severity:
        query = query.where(incidents.c.severity == severity)

    # Order by created_at descending — newest incidents first
    query = query.order_by(incidents.c.id.desc())

    # Execute and fetch all matching rows
    rows = await database.fetch_all(query)

    # Convert each database row to a dict (required for JSON serialization)
    return [dict(row) for row in rows]


# ============================================================
# GET /incidents/stats — Aggregate statistics  ← NEW DAY 41
# ============================================================
# MUST be defined BEFORE GET /incidents/{id}
# If /{id} is defined first, "stats" gets treated as an ID parameter

@router.get("/stats")
async def get_incident_stats():
    """
    Return aggregate counts of all incidents in the database.

    Used by the frontend StatsBar component to show:
    - Total number of incidents
    - Counts by severity (critical/high/medium/low)
    - Counts by status (pending/active/resolved)
    - Counts by incident type (fire/medical/crime/etc.)
    - High-risk incident count (risk_score > 0.7)
    - Count with audio attachments

    All counts come from a SINGLE database query using CASE WHEN expressions.
    This is much faster than running a separate COUNT query for each statistic.
    """

    # ── BUILD THE AGGREGATE QUERY ─────────────────────────
    # We use sqlalchemy's select() with func.count() and case() to build
    # a single SQL query that returns all statistics at once.
    #
    # The resulting SQL looks approximately like:
    #
    #   SELECT
    #     COUNT(*) as total,
    #     COUNT(CASE WHEN severity='critical' THEN 1 END) as critical_count,
    #     COUNT(CASE WHEN severity='high' THEN 1 END) as high_count,
    #     ...
    #   FROM incidents
    #
    # Running one query is faster than running 10+ separate queries.

    stats_query = select(

        # Total number of incidents in the database
        # func.count() with no argument counts all rows
        func.count().label("total"),

        # ── BY SEVERITY ────────────────────────────────────
        # case() creates a conditional expression:
        # "If severity = 'critical', count this row, otherwise skip it"
        func.count(
            case((incidents.c.severity == "critical", 1))
        ).label("critical_count"),

        func.count(
            case((incidents.c.severity == "high", 1))
        ).label("high_count"),

        func.count(
            case((incidents.c.severity == "medium", 1))
        ).label("medium_count"),

        func.count(
            case((incidents.c.severity == "low", 1))
        ).label("low_count"),

        # ── BY STATUS ──────────────────────────────────────
        func.count(
            case((incidents.c.status == "pending", 1))
        ).label("pending_count"),

        func.count(
            case((incidents.c.status == "active", 1))
        ).label("active_count"),

        func.count(
            case((incidents.c.status == "resolved", 1))
        ).label("resolved_count"),

        # ── BY INCIDENT TYPE ───────────────────────────────
        func.count(
            case((incidents.c.incident_type == "fire", 1))
        ).label("fire_count"),

        func.count(
            case((incidents.c.incident_type == "medical", 1))
        ).label("medical_count"),

        func.count(
            case((incidents.c.incident_type == "crime", 1))
        ).label("crime_count"),

        func.count(
            case((incidents.c.incident_type == "traffic", 1))
        ).label("traffic_count"),

        func.count(
            case((incidents.c.incident_type == "infrastructure", 1))
        ).label("infrastructure_count"),

        func.count(
            case((incidents.c.incident_type == "other", 1))
        ).label("other_count"),

        # ── SPECIAL COUNTS ─────────────────────────────────
        # High-risk: risk_score above 0.7 (shown as red in the UI)
        func.count(
            case((incidents.c.risk_score > 0.7, 1))
        ).label("high_risk_count"),

        # With audio: incidents that have an audio file attached
        # is not None checks that audio_path has a value
        func.count(
            case((incidents.c.audio_path != None, 1))
        ).label("with_audio_count"),

    # .select_from() tells SQLAlchemy which table to query
    ).select_from(incidents)

    # Execute the query — returns exactly one row with all the counts
    row = await database.fetch_one(stats_query)

    # If database is empty, row will still exist but all counts will be 0
    # Convert the row to a dict so we can restructure it
    raw = dict(row)

    # ── STRUCTURE THE RESPONSE ────────────────────────────
    # Instead of returning all the flat keys (high_count, low_count, etc.)
    # we nest them into logical groups. This makes the frontend code cleaner:
    # stats.by_severity.high instead of stats.high_count

    return {
        # The top-level total
        "total": raw["total"],

        # Severity breakdown — nested dict
        "by_severity": {
            "critical": raw["critical_count"],
            "high":     raw["high_count"],
            "medium":   raw["medium_count"],
            "low":      raw["low_count"],
        },

        # Status breakdown — nested dict
        "by_status": {
            "pending":  raw["pending_count"],
            "active":   raw["active_count"],
            "resolved": raw["resolved_count"],
        },

        # Incident type breakdown — nested dict
        "by_type": {
            "fire":           raw["fire_count"],
            "medical":        raw["medical_count"],
            "crime":          raw["crime_count"],
            "traffic":        raw["traffic_count"],
            "infrastructure": raw["infrastructure_count"],
            "other":          raw["other_count"],
        },

        # Special metrics — top-level for easy access
        "high_risk_count":  raw["high_risk_count"],
        "with_audio_count": raw["with_audio_count"],
    }


# ============================================================
# GET /incidents/{id} — Get a single incident by ID
# ============================================================
# Defined AFTER /stats so "stats" isn't treated as an ID

@router.get("/{incident_id}", response_model=IncidentRead)
async def get_incident(incident_id: int):
    """
    Fetch a single incident by its database ID.
    Returns 404 if no incident with that ID exists.
    """

    # Build SELECT query with WHERE id = incident_id
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)

    if not incident:
        # No row found — return HTTP 404 Not Found
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return dict(incident)


# ============================================================
# PATCH /incidents/{id} — Update an incident's fields
# ============================================================

@router.patch("/{incident_id}", response_model=IncidentRead)
async def update_incident(incident_id: int, update_data: IncidentUpdate):
    """
    Partially update an incident.
    Only the fields included in the request body are changed.
    Used by the frontend to update status (pending/active/resolved).
    """

    # Verify the incident exists before trying to update it
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Build a dict of only the fields that were provided in the request
    # exclude_unset=True means "don't include fields not sent by the client"
    # This prevents accidentally overwriting fields with None
    update_fields = update_data.model_dump(exclude_unset=True)

    if not update_fields:
        # Request body was empty — nothing to update
        raise HTTPException(status_code=400, detail="No fields provided to update")

    # Build and execute the UPDATE query
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(**update_fields)
    )
    await database.execute(update_query)

    # Fetch and return the updated incident
    updated = await database.fetch_one(check_query)
    return dict(updated)


# ============================================================
# DELETE /incidents/{id} — Delete an incident
# ============================================================

@router.delete("/{incident_id}", status_code=204)
async def delete_incident(incident_id: int):
    """
    Permanently delete an incident from the database.
    Returns 204 No Content on success.
    """

    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    delete_query = incidents.delete().where(incidents.c.id == incident_id)
    await database.execute(delete_query)

    # 204 responses have no body — just return None
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
    """
    Upload an audio file to an existing incident.
    Triggers AI processing (transcription) in the background.
    """

    # Verify incident exists
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Validate file type — only accept audio formats
    allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", "audio/x-m4a"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Must be audio."
        )

    # Save the uploaded file to disk with a unique UUID filename
    file_path = await save_upload_file(file, subfolder="audio")

    # Update the incident's audio_path in the database
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(audio_path=file_path)
    )
    await database.execute(update_query)

    # Trigger AI processing in the background (transcription + rest of pipeline)
    background_tasks.add_task(
        process_incident,
        incident_id,
        "Audio uploaded — re-processing"
    )

    return {
        "message": "Audio uploaded successfully",
        "file_path": file_path,
        "incident_id": incident_id,
    }


# ============================================================
# POST /incidents/{id}/image — Upload image file
# ============================================================


@router.post("/{incident_id}/image")
async def upload_image(
    incident_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
):
    """
    Upload an image file to an existing incident.
    """

    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)

    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Validate file type — only accept image formats
    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/heif"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type: {file.content_type}. Must be an image."
        )

    # Save file to disk
    file_path = await save_upload_file(file, subfolder="images")

    # Update the incident's image_path
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(image_path=file_path)
    )
    await database.execute(update_query)



    background_tasks.add_task(
        process_incident,
        incident_id,
        "Image uploaded — re-processing"
    )

    return {
        "message": "Image uploaded successfully",
        "file_path": file_path,
        "incident_id": incident_id,
    }




