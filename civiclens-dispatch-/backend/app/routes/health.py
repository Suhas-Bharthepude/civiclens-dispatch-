# backend/app/routes/health.py
#
# Health check endpoints for CivicLens Dispatch.
# Two endpoints:
#
#   GET /health          — Quick API liveness check (already existed)
#                          Returns: {"status": "ok", "service": "..."}
#
#   GET /health/pipeline — AI services status check (NEW Day 43)
#                          Returns: status of each AI service + database info
#
# Health checks are deliberately FAST — they don't call AI APIs.
# They just verify configuration (API keys, mock flags) and DB connectivity.
# A real API call would take 10+ seconds, which defeats the purpose.

# FastAPI router for creating grouped endpoints
from fastapi import APIRouter

# datetime for showing when the health check ran
from datetime import datetime

# Our database connection — used to count incidents
from app.db.database import database

# The incidents table — used to build the COUNT query
from app.db.models import incidents

# SQLAlchemy's func gives us SQL aggregate functions like COUNT()
from sqlalchemy import func, select

# Import each service's mock flag and configuration
# We check these to determine if each service is in mock or real mode
from app.services.asr            import USE_MOCK_TRANSCRIPTION
from app.services.summarization  import USE_MOCK_SUMMARIZATION
from app.services.classification import USE_MOCK_CLASSIFICATION
from app.services.image_analysis import USE_MOCK_IMAGE_ANALYSIS

# Settings gives us access to the HUGGINGFACE_API_KEY env variable
from app.config import settings

# Create the router
# No prefix here — health routes are registered directly in main.py
router = APIRouter(tags=["health"])


# ============================================================
# GET /health — Quick liveness check (unchanged from before)
# ============================================================

@router.get("/health")
async def health_check():
    """
    Basic liveness check — confirms the API is running and reachable.
    Called by the frontend HealthCheck component every 30 seconds.
    Returns instantly — no database or AI calls.
    """
    return {
        "status": "ok",
        "service": "CivicLens Dispatch API",
        "version": "1.0.0",
    }


# ============================================================
# GET /health/pipeline — AI services + database status
# ============================================================

@router.get("/health/pipeline")
async def pipeline_health():
    """
    Detailed health check for all AI services and the database.

    Checks:
      - Whether each AI service is in real or mock mode
      - Whether the Hugging Face API key is configured
      - Database connectivity and current incident count

    Does NOT call any AI APIs — just checks configuration.
    This makes it fast (< 100ms response time).

    Response shape:
    {
      "status": "healthy" | "degraded" | "error",
      "checked_at": "2025-03-31T14:22:00",
      "services": {
        "asr":            {"status": "mock"|"ok"|"error", "model": "...", "note": "..."},
        "classification": {"status": "mock"|"ok"|"error", "model": "...", "note": "..."},
        "summarization":  {"status": "mock"|"ok"|"error", "model": "...", "note": "..."},
        "image_analysis": {"status": "mock"|"ok"|"error", "model": "...", "note": "..."},
      },
      "database": {"status": "ok"|"error", "incident_count": 25},
      "api_key_configured": true | false
    }
    """

    # ── CHECK API KEY ─────────────────────────────────────
    # Check if the Hugging Face API key is set in .env
    # We don't validate the key (that would require a network call)
    # We just check it exists and isn't the placeholder value
    api_key = getattr(settings, "HUGGINGFACE_API_KEY", None)
    api_key_configured = bool(
        api_key
        and api_key != "your_huggingface_api_key_here"
        and len(api_key) > 10
    )

    # ── CHECK EACH AI SERVICE ─────────────────────────────
    # For each service, determine its status based on:
    #   - "mock"  → mock flag is True (by design, not a failure)
    #   - "ok"    → real mode, API key configured
    #   - "error" → real mode attempted but no API key

    def service_status(is_mock: bool, model_name: str, description: str) -> dict:
        """
        Helper that builds a status dict for one AI service.

        Args:
            is_mock:     True if the service's USE_MOCK_* flag is True
            model_name:  The Hugging Face model name (for display)
            description: Human-readable description of what the service does
        """
        if is_mock:
            # Mock mode — working but not using real AI
            return {
                "status": "mock",
                "model": model_name,
                "description": description,
                "note": "Mock mode active — returns placeholder output",
            }
        elif not api_key_configured:
            # Real mode requested but no API key — this won't work
            return {
                "status": "error",
                "model": model_name,
                "description": description,
                "note": "HUGGINGFACE_API_KEY not configured in .env",
            }
        else:
            # Real mode with API key — should work
            return {
                "status": "ok",
                "model": model_name,
                "description": description,
                "note": "Real AI mode — calls Hugging Face API",
            }

    # Build status for each of the four AI services
    services = {
        # ASR: audio → text using Whisper
        "asr": service_status(
            is_mock=USE_MOCK_TRANSCRIPTION,
            model_name="openai/whisper-large-v3-turbo",
            description="Audio transcription (speech-to-text)",
        ),
        # Classification: text → type + severity using BART-MNLI
        "classification": service_status(
            is_mock=USE_MOCK_CLASSIFICATION,
            model_name="facebook/bart-large-mnli",
            description="Incident type and severity classification",
        ),
        # Summarization: text → summary paragraph using BART-CNN
        "summarization": service_status(
            is_mock=USE_MOCK_SUMMARIZATION,
            model_name="facebook/bart-large-cnn",
            description="Incident summary generation",
        ),
        # Image analysis: image → description using BLIP
        "image_analysis": service_status(
            is_mock=USE_MOCK_IMAGE_ANALYSIS,
            model_name="Salesforce/blip-image-captioning-base",
            description="Photo description generation",
        ),
    }

    # ── CHECK DATABASE ────────────────────────────────────
    # Try to run a simple COUNT query to verify DB is responsive
    try:
        # COUNT(*) returns the total number of rows in the incidents table
        count_query = select(func.count()).select_from(incidents)
        count = await database.fetch_val(count_query)

        db_status = {
            "status": "ok",
            "incident_count": count,
            "note": "Database connected and responsive",
        }
    except Exception as e:
        # Database query failed — something is wrong with the connection
        db_status = {
            "status": "error",
            "incident_count": None,
            "note": f"Database error: {str(e)[:100]}",
        }

    # ── DETERMINE OVERALL STATUS ──────────────────────────
    # Overall status is based on the worst individual status:
    #   - "healthy"  → all services ok or mock, database ok
    #   - "degraded" → some services in mock mode (expected during development)
    #   - "error"    → any service has an error, or database failed

    # Collect all individual status values
    all_statuses = [svc["status"] for svc in services.values()]
    all_statuses.append(db_status["status"])

    if "error" in all_statuses:
        # At least one service has a real error
        overall = "error"
    elif "mock" in all_statuses:
        # Some services are mocked — degraded but functional
        overall = "degraded"
    else:
        # Everything is in real mode and configured
        overall = "healthy"

    # ── BUILD AND RETURN RESPONSE ─────────────────────────
    return {
        # Overall system status
        "status": overall,

        # When this check ran (ISO format)
        "checked_at": datetime.utcnow().isoformat(),

        # Whether the HF API key is present in .env
        "api_key_configured": api_key_configured,

        # Status of each AI service
        "services": services,

        # Database connectivity
        "database": db_status,
    }