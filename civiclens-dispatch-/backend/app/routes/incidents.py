# backend/app/routes/incidents.py
#
# FastAPI route handlers for /incidents endpoints.
# Day 44: Added `search` query parameter to GET /incidents
#         Searches description, location, transcript, and summary using LIKE.
#
# Route order (IMPORTANT — specific before parameterized):
#   POST   /incidents          → create_incident
#   GET    /incidents          → list_incidents  ← search added here
#   GET    /incidents/stats    → get_incident_stats
#   GET    /incidents/{id}     → get_incident
#   PATCH  /incidents/{id}     → update_incident
#   DELETE /incidents/{id}     → delete_incident
#   POST   /incidents/{id}/audio → upload_audio
#   POST   /incidents/{id}/image → upload_image

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks
from sqlalchemy import func, select, case, or_
# or_ lets us combine multiple WHERE conditions with OR
# e.g. WHERE description LIKE '%fire%' OR location LIKE '%fire%'

from datetime import datetime
# datetime is used to set created_at when creating new incidents

from app.db.database import database
from app.db.models import incidents
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentRead
from app.services.incident_processor import process_incident
from app.utils.file_utils import save_upload_file
import uuid

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
    """

    # Build INSERT with all initial fields
    # AI fields (transcript, summary, etc.) start as None
    # The background pipeline fills them in after creation
    insert_query = incidents.insert().values(
        description=incident_data.description,
        source=incident_data.source,
        location=incident_data.location,
        # Set status to "pending" for all new incidents
        status="pending",
        # Set created_at to the current UTC time
        # datetime.utcnow() returns the current time in UTC (no timezone offset)
        # Always use UTC for storage — the frontend converts to local time
        created_at=datetime.utcnow(),
        # All AI fields start as None — pipeline fills these in
        transcript=None,
        summary=None,
        risk_score=None,
        incident_type=None,
        severity=None,
        audio_path=None,
        image_path=None,
        image_description=None,
    )

    # Execute the INSERT and get the new row's auto-generated ID
    new_id = await database.execute(insert_query)

    # Fetch the complete new incident to return in the response
    select_query = incidents.select().where(incidents.c.id == new_id)
    new_incident = await database.fetch_one(select_query)

    # Schedule AI processing to run in the background
    # Returns immediately — AI processing happens separately
    background_tasks.add_task(
        process_incident,
        new_id,
        "New incident created"
    )

    return dict(new_incident)


# ============================================================
# GET /incidents — List incidents with optional filters + search
# ============================================================

@router.get("", response_model=list[IncidentRead])
async def list_incidents(
    # Optional filter: show only incidents with this status
    status: str = None,
    # Optional filter: show only incidents of this type
    incident_type: str = None,
    # Optional filter: show only incidents with this severity
    severity: str = None,
    # Optional search: full-text search across multiple fields  ← NEW DAY 44
    # When provided, returns incidents where description, location,
    # transcript, or summary contains this string (case-insensitive)
    search: str = None,
):
    """
    Fetch all incidents. Supports filtering by status/type/severity
    and keyword search across description, location, transcript, and summary.

    Query parameters:
      ?status=pending         — filter by status
      ?incident_type=fire     — filter by type
      ?severity=high          — filter by severity
      ?search=oak+street      — search keyword across multiple fields

    Filters can be combined: ?incident_type=fire&search=oak+street
    """

    # Start with a basic SELECT * FROM incidents
    query = incidents.select()

    # ── APPLY EXACT-MATCH FILTERS ─────────────────────────
    # These are the existing filters — nothing changed here
    if status:
        query = query.where(incidents.c.status == status)
    if incident_type:
        query = query.where(incidents.c.incident_type == incident_type)
    if severity:
        query = query.where(incidents.c.severity == severity)

    # ── APPLY SEARCH ─────────────────────────────────────  ← NEW DAY 44
    # If a search term was provided, add a WHERE condition that checks
    # multiple columns using OR (match any of them, not all of them)
    if search and search.strip():
        # Strip whitespace from both ends of the search term
        # "  oak street  " becomes "oak street"
        search_term = search.strip()

        # Build the LIKE pattern: %searchterm%
        # The % wildcards mean "any characters before and after"
        # So "%oak%" matches "oak", "Oak Street", "near oak park", etc.
        like_pattern = f"%{search_term}%"

        # ilike() is SQLAlchemy's case-insensitive LIKE
        # It handles lowercase conversion for us — no need for LOWER()
        # "Fire" matches "%fire%" because ilike is case-insensitive
        #
        # or_() combines multiple conditions with SQL OR
        # We want to match if ANY of these columns contains the search term
        search_condition = or_(
            # Search in the human-written description
            incidents.c.description.ilike(like_pattern),
            # Search in the location field
            incidents.c.location.ilike(like_pattern),
            # Search in the AI-generated transcript (may be None — ilike handles this)
            incidents.c.transcript.ilike(like_pattern),
            # Search in the AI-generated summary (may be None)
            incidents.c.summary.ilike(like_pattern),
        )

        # Add the search condition to the query
        # Combined with the other filters using AND:
        # e.g. "WHERE incident_type='fire' AND (description LIKE '%oak%' OR location LIKE '%oak%')"
        query = query.where(search_condition)

    # Order by id descending — newest incidents first
    # We use id instead of created_at because older incidents had NULL created_at
    query = query.order_by(incidents.c.id.desc())

    # Execute and fetch all matching rows
    rows = await database.fetch_all(query)

    # Convert each database row to a dict for JSON serialization
    return [dict(row) for row in rows]


# ============================================================
# GET /incidents/stats — Aggregate statistics
# ============================================================
# MUST be before /{incident_id} to avoid "stats" being treated as an ID

@router.get("/stats")
async def get_incident_stats():
    """
    Return aggregate counts of all incidents.
    Used by the StatsBar component.
    """

    stats_query = select(
        func.count().label("total"),
        func.count(case((incidents.c.severity == "critical", 1))).label("critical_count"),
        func.count(case((incidents.c.severity == "high", 1))).label("high_count"),
        func.count(case((incidents.c.severity == "medium", 1))).label("medium_count"),
        func.count(case((incidents.c.severity == "low", 1))).label("low_count"),
        func.count(case((incidents.c.status == "pending", 1))).label("pending_count"),
        func.count(case((incidents.c.status == "active", 1))).label("active_count"),
        func.count(case((incidents.c.status == "resolved", 1))).label("resolved_count"),
        func.count(case((incidents.c.incident_type == "fire", 1))).label("fire_count"),
        func.count(case((incidents.c.incident_type == "medical", 1))).label("medical_count"),
        func.count(case((incidents.c.incident_type == "crime", 1))).label("crime_count"),
        func.count(case((incidents.c.incident_type == "traffic", 1))).label("traffic_count"),
        func.count(case((incidents.c.incident_type == "infrastructure", 1))).label("infrastructure_count"),
        func.count(case((incidents.c.incident_type == "other", 1))).label("other_count"),
        func.count(case((incidents.c.risk_score > 0.7, 1))).label("high_risk_count"),
        func.count(case((incidents.c.audio_path != None, 1))).label("with_audio_count"),
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
        "by_status": {
            "pending":  raw["pending_count"],
            "active":   raw["active_count"],
            "resolved": raw["resolved_count"],
        },
        "by_type": {
            "fire":           raw["fire_count"],
            "medical":        raw["medical_count"],
            "crime":          raw["crime_count"],
            "traffic":        raw["traffic_count"],
            "infrastructure": raw["infrastructure_count"],
            "other":          raw["other_count"],
        },
        "high_risk_count":  raw["high_risk_count"],
        "with_audio_count": raw["with_audio_count"],
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
    """Partially update an incident (used for status changes)."""

    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # exclude_unset=True means only include fields the client actually sent
    # This prevents accidentally overwriting fields with None
    update_fields = update_data.model_dump(exclude_unset=True)
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(**update_fields)
    )
    await database.execute(update_query)

    updated = await database.fetch_one(check_query)
    return dict(updated)


# ============================================================
# DELETE /incidents/{id}
# ============================================================

@router.delete("/{incident_id}", status_code=204)
async def delete_incident(incident_id: int):
    """Permanently delete an incident."""
    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
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

    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    allowed_types = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", "audio/x-m4a"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")

    file_path = await save_upload_file(file, subfolder="audio")

    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(audio_path=file_path)
    )
    await database.execute(update_query)

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

    check_query = incidents.select().where(incidents.c.id == incident_id)
    existing = await database.fetch_one(check_query)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/heic", "image/heif"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Invalid file type: {file.content_type}")

    file_path = await save_upload_file(file, subfolder="images")

    update_query = (
        incidents.update()
        .where(incidents.c.id == incident_id)
        .values(image_path=file_path)
    )
    await database.execute(update_query)

    # Re-trigger pipeline so image analysis runs on the new photo
    background_tasks.add_task(process_incident, incident_id, "Image uploaded — re-processing")

    return {"message": "Image uploaded successfully", "file_path": file_path, "incident_id": incident_id}





# Import BackgroundTasks if not already imported at the top of the file
# It should already be there from the create incident endpoint
# from fastapi import BackgroundTasks

# Import process_incident if not already imported at the top
# from app.services.incident_processor import process_incident


# ========================================
# REPROCESS ENDPOINT
# ========================================

@router.post("/{incident_id}/reprocess")
async def reprocess_incident(
    incident_id: int,
    background_tasks: BackgroundTasks
):
    """
    Re-run the full AI pipeline on an existing incident.
    
    Use this when:
    - Original AI processing failed (timeout, rate limit, model down)
    - Incident was updated and needs re-analysis
    - AI models have been improved and you want fresh results
    
    The AI pipeline runs in the background (same as initial processing).
    The endpoint returns immediately with a confirmation message.
    
    Args:
        incident_id: The ID of the incident to reprocess
        background_tasks: FastAPI's BackgroundTasks for async execution
    
    Returns:
        JSON confirmation that reprocessing has been queued
    """
    
    # First, check if the incident exists in the database
    # We don't want to queue a reprocess for a non-existent incident
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)
    
    # If incident doesn't exist, return 404 error
    if not incident:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"Incident {incident_id} not found"
        )
    
    # Queue the AI pipeline to run in the background
    # This is the same function that runs when an incident is first created
    # background_tasks.add_task() schedules it to run after the response is sent
    background_tasks.add_task(
        process_incident,
        incident_id,
        f"Reprocessing incident {incident_id} (manual trigger)"
    )
    
    # Return confirmation immediately (don't wait for AI processing)
    return {
        "message": f"Reprocessing queued for incident {incident_id}",
        "incident_id": incident_id,
        "status": "queued",
        "note": "AI pipeline will run in the background. Refresh to see updated results."
    }