# backend/app/routes/analytics.py
# Analytics endpoint that provides aggregate statistics about incidents
#
# Endpoint: GET /analytics/summary
# Returns counts by type, by severity, average risk scores,
# and media attachment statistics.
#
# This gives dispatchers and administrators a high-level view
# of incident patterns without fetching all individual records.
#
# Day 55: Analytics and observability

# Import APIRouter from FastAPI to create a router for analytics endpoints
from fastapi import APIRouter

# Import database connection for running queries
from app.db.database import database

# Import incidents table for building SQL queries
from app.db.models import incidents

# Import sqlalchemy functions for aggregate queries (COUNT, AVG, etc.)
from sqlalchemy import func, case, select

# Import our logging configuration
from app.logging_config import get_logger

# Create a logger for this module
logger = get_logger(__name__)


# ========================================
# ROUTER SETUP
# ========================================

# Create a router with /analytics prefix
# All endpoints in this file will start with /analytics
router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


# ========================================
# ANALYTICS SUMMARY ENDPOINT
# ========================================

@router.get("/summary")
async def get_analytics_summary():
    """
    Get aggregate statistics about all incidents.
    
    Returns:
        JSON with:
        - total_incidents: Total count
        - by_type: Count per incident type (fire, medical, etc.)
        - by_severity: Count per severity level (high, medium, low)
        - avg_risk_score: Average risk score across all incidents
        - with_audio: Count of incidents that have audio files
        - with_images: Count of incidents that have image files
        - with_summary: Count of incidents that have AI summaries
        - ai_processed: Count of incidents fully processed by AI
    """
    
    logger.info("Generating analytics summary")
    
    # ── TOTAL COUNT ───────────────────────────────────
    # Count all incidents in the database
    total_query = select(func.count()).select_from(incidents)
    total = await database.fetch_val(total_query)
    
    # ── COUNT BY TYPE ─────────────────────────────────
    # Group incidents by incident_type and count each group
    # Result: [{"type": "fire", "count": 5}, {"type": "medical", "count": 3}, ...]
    type_query = (
        select(
            incidents.c.incident_type,
            func.count().label("count")
        )
        .group_by(incidents.c.incident_type)
        .order_by(func.count().desc())
    )
    type_rows = await database.fetch_all(type_query)
    
    # Convert rows to a dictionary: {"fire": 5, "medical": 3, ...}
    by_type = {}
    for row in type_rows:
        # Use "unclassified" for incidents where type is None
        type_name = row["incident_type"] or "unclassified"
        by_type[type_name] = row["count"]
    
    # ── COUNT BY SEVERITY ─────────────────────────────
    # Group incidents by severity and count each group
    severity_query = (
        select(
            incidents.c.severity,
            func.count().label("count")
        )
        .group_by(incidents.c.severity)
        .order_by(func.count().desc())
    )
    severity_rows = await database.fetch_all(severity_query)
    
    # Convert to dictionary: {"high": 4, "medium": 5, "low": 1}
    by_severity = {}
    for row in severity_rows:
        sev_name = row["severity"] or "unclassified"
        by_severity[sev_name] = row["count"]
    
    # ── AVERAGE RISK SCORE ────────────────────────────
    # Calculate the average risk_score across all incidents that have one
    avg_risk_query = select(
        func.avg(incidents.c.risk_score)
    ).where(incidents.c.risk_score.isnot(None))
    avg_risk = await database.fetch_val(avg_risk_query)
    
    # Round to 4 decimal places, default to 0 if no scores exist
    avg_risk = round(avg_risk, 4) if avg_risk else 0.0
    
    # ── MEDIA COUNTS ──────────────────────────────────
    # Count how many incidents have audio files attached
    audio_query = select(func.count()).select_from(incidents).where(
        incidents.c.audio_path.isnot(None)
    )
    with_audio = await database.fetch_val(audio_query)
    
    # Count how many incidents have image files attached
    image_query = select(func.count()).select_from(incidents).where(
        incidents.c.image_path.isnot(None)
    )
    with_images = await database.fetch_val(image_query)
    
    # ── AI PROCESSING COUNTS ──────────────────────────
    # Count how many incidents have AI summaries (meaning pipeline ran)
    summary_query = select(func.count()).select_from(incidents).where(
        incidents.c.summary.isnot(None)
    )
    with_summary = await database.fetch_val(summary_query)
    
    # Count fully AI-processed incidents (have type + severity + risk + summary)
    processed_query = select(func.count()).select_from(incidents).where(
        incidents.c.incident_type.isnot(None),
        incidents.c.severity.isnot(None),
        incidents.c.risk_score.isnot(None),
        incidents.c.summary.isnot(None),
    )
    ai_processed = await database.fetch_val(processed_query)
    
    # ── BUILD RESPONSE ────────────────────────────────
    summary = {
        "total_incidents": total,
        "by_type": by_type,
        "by_severity": by_severity,
        "avg_risk_score": avg_risk,
        "with_audio": with_audio,
        "with_images": with_images,
        "with_summary": with_summary,
        "ai_processed": ai_processed,
    }
    
    logger.info(
        "Analytics: %d total, %d AI-processed, avg risk %.2f",
        total, ai_processed, avg_risk
    )
    
    return summary