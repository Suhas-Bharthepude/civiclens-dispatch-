# backend/app/main.py
# Main entry point for the CivicLens Dispatch FastAPI application.
# Creates the app, registers routes, configures middleware, and manages
# the database connection lifecycle (connect on startup, disconnect on shutdown).
#
# Day 67: Updated to use environment-aware config for CORS, docs, and debug mode.

# Import FastAPI core
from fastapi import FastAPI

# Import CORS middleware — allows the React frontend to call this API
from fastapi.middleware.cors import CORSMiddleware

# Import database tools
from app.db.database import database, engine, metadata

# Import tables so they register with metadata (needed for create_all)
# Both incidents and users tables must be imported before metadata.create_all()
from app.db.models import incidents, users  # noqa: F401

# Import config — settings reads from .env and adjusts based on ENVIRONMENT
# configure_logging sets up Python logging based on environment
# print_startup_summary prints a readable config summary in development only
from app.config import settings, configure_logging, print_startup_summary

# Import routers — each handles a different group of endpoints
from app.routes.incidents import router as incidents_router
from app.routes.ai_status import router as ai_status_router
from app.routes.analytics import router as analytics_router
# WebSocket router — provides /ws/incidents for real-time browser updates (Day 71)
from app.routes.ws_routes import router as ws_router
# Auth router — login, register, /auth/me (Day 72)
from app.routes.auth_routes import router as auth_router

# Import global exception handlers — catch errors and return clean JSON
from app.error_handlers import register_exception_handlers

# Import request logging middleware — logs each incoming request
from app.middleware import RequestLoggingMiddleware

# Import logging setup — configures Python's logging system
from app.logging_config import setup_logging

# Import file utilities — ensures upload directories exist on startup
from app.utils.file_utils import ensure_upload_dirs


# ========================================
# CREATE DATABASE TABLES
# ========================================

# Runs once when this module is imported.
# Creates all tables defined in metadata if they don't already exist.
# Uses the sync engine because create_all() is a synchronous operation.

try:
    metadata.create_all(engine)
except Exception as e:
    print(f"⚠️  Table creation skipped: {e}")

# ========================================
# CONFIGURE LOGGING
# ========================================

# Set up Python's logging system based on the current environment.
# Development: DEBUG level (verbose — shows everything)
# Production: WARNING level (only shows problems)
configure_logging()

# Print a human-readable config summary to the terminal.
# Only runs in development mode — skipped automatically in production.
print_startup_summary()


# ========================================
# CREATE FASTAPI APPLICATION
# ========================================

# Set up logging for uvicorn using our logging config
setup_logging(settings.LOG_LEVEL)

app = FastAPI(
    # App name shown in the auto-generated API docs (/docs)
    title=settings.APP_TITLE,

    # Version string shown in API docs
    version=settings.VERSION,

    # Debug mode — when True, FastAPI shows detailed error tracebacks
    # effective_debug forces this to False in production even if DEBUG=True in .env
    debug=settings.effective_debug,

    # Only show /docs and /redoc in development
    # In production, hiding the docs is a minor security improvement
    # (no need to advertise your API structure publicly)
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)


# ========================================
# CONFIGURE CORS
# ========================================

# CORS (Cross-Origin Resource Sharing) controls which websites can call this API.
# Without this, the browser blocks requests from the React frontend (different port).
app.add_middleware(
    CORSMiddleware,

    # effective_cors_origins returns ["*"] in development (allow everything)
    # and the specific frontend URL(s) in production (restrict to your app only)
    allow_origins=settings.effective_cors_origins,

    # Allow cookies and auth headers to be sent with requests
    allow_credentials=True,

    # Allow all HTTP methods (GET, POST, PATCH, DELETE, etc.)
    allow_methods=["*"],

    # Allow all headers
    allow_headers=["*"],
)

# Add request logging middleware — logs method, path, and response time
app.add_middleware(RequestLoggingMiddleware)


# ========================================
# REGISTER ROUTERS
# ========================================

# Incidents router — all /incidents endpoints (CRUD, uploads, reprocess, stats)
app.include_router(
    incidents_router,
    prefix="",   # No extra prefix — routes already include /incidents
    tags=["incidents"]
)

# AI status router — GET /ai/status (checks all 4 Hugging Face models)
app.include_router(ai_status_router)

# Analytics router — GET /incidents/analytics/* aggregate endpoints
app.include_router(analytics_router)

# WebSocket router — ws://host/ws/incidents for real-time browser updates (Day 71)
app.include_router(ws_router)

# Auth router — POST /auth/login, /auth/register, GET /auth/me (Day 72)
app.include_router(auth_router)

# Register global exception handlers — catches unhandled errors and returns JSON
register_exception_handlers(app)


# ========================================
# APPLICATION LIFECYCLE
# ========================================

@app.on_event("startup")
async def startup_event():
    """
    Runs once when the server starts.
    Connects to the database and ensures upload directories exist.
    """
    # Connect the async database — must happen before any queries run
    await database.connect()
    print(f"✅ Database connected: {settings.DATABASE_URL}")

    # Create upload directories (app/media/tmp/audio, /images) if missing
    ensure_upload_dirs()

    print(f"✅ {settings.APP_TITLE} v{settings.VERSION} started [{settings.ENVIRONMENT}]")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs once when the server shuts down.
    Disconnects from the database cleanly.
    """
    # Disconnect the async database — prevents connection leaks
    await database.disconnect()
    print("❌ Database disconnected")
    print("❌ Application shut down")


# ========================================
# ROOT ENDPOINTS
# ========================================

@app.head("/")
async def root_head():
    return {}


@app.get("/")
async def root():
    """
    Root endpoint — confirms the API is running.
    Returns app name, version, and a link to the docs.
    """
    return {
        "message": "CivicLens Dispatch API is running",
        "version": settings.VERSION,
        "docs": "/docs" if settings.is_development else "disabled in production",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Used by monitoring tools, load balancers, and the frontend to confirm
    the backend is alive. Always returns 200 OK if the server is running.
    """
    return {
        "status": "ok",
        "service": settings.APP_TITLE,
        "version": settings.VERSION,
    }


@app.get("/config")
async def get_config():
    """
    Show current configuration (no secrets).
    Useful for verifying which environment is active after deploying.
    The database URL is partially masked to avoid exposing credentials.
    """
    return {
        "app_title": settings.APP_TITLE,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,

        # Use effective_debug so this always shows the real runtime value
        "debug": settings.effective_debug,

        # Mask credentials from the DB URL — only show the host/db portion
        "database": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,

        # Show the actual CORS origins being enforced
        "cors_origins": settings.effective_cors_origins,

        # Show effective log level (may differ from LOG_LEVEL setting in prod)
        "log_level": settings.effective_log_level,

        "upload_dir": settings.UPLOAD_DIR,

        # Convert bytes to MB for readability
        "max_upload_size_mb": settings.MAX_UPLOAD_SIZE / (1024 * 1024),

        # Only show whether the key is set — never expose the actual token
        "huggingface_key_set": bool(settings.HUGGINGFACE_API_KEY),

        "use_mock_ai": settings.USE_MOCK_AI,
    }


@app.get("/health/pipeline")
async def pipeline_health():
    """
    Detailed health check for the AI pipeline.
    Shows whether each AI service is using real models or mocks,
    and confirms the database is reachable.
    """
    from app.services.asr import USE_MOCK_TRANSCRIPTION
    from app.services.summarization import USE_MOCK_SUMMARIZATION
    from app.services.classification import USE_MOCK_CLASSIFICATION
    from app.services.image_analysis import USE_MOCK_IMAGE_ANALYSIS
    from datetime import datetime
    from sqlalchemy import func, select as sa_select

    # Build a status dict for each AI service
    services = {
        "asr":            {"status": "mock" if USE_MOCK_TRANSCRIPTION else "ok",  "model": "openai/whisper-large-v3-turbo"},
        "classification": {"status": "mock" if USE_MOCK_CLASSIFICATION else "ok", "model": "facebook/bart-large-mnli"},
        "summarization":  {"status": "mock" if USE_MOCK_SUMMARIZATION else "ok",  "model": "facebook/bart-large-cnn"},
        "image_analysis": {"status": "mock" if USE_MOCK_IMAGE_ANALYSIS else "ok", "model": "Salesforce/blip-image-captioning-base"},
    }

    # Check database by counting incidents
    try:
        count = await database.fetch_val(sa_select(func.count()).select_from(incidents))
        db = {"status": "ok", "incident_count": count}
    except Exception:
        db = {"status": "error", "incident_count": None}

    # Determine overall status
    statuses = [s["status"] for s in services.values()]
    overall = "error" if "error" in statuses else "degraded" if "mock" in statuses else "healthy"

    return {
        "status": overall,
        "checked_at": datetime.utcnow().isoformat(),
        "services": services,
        "database": db,
    }


@app.get("/echo/{name}")
async def echo_name(name: str):
    """
    Echo endpoint — demonstrates path parameters.
    Example: GET /echo/Alice → {"hello": "Alice"}
    """
    return {"hello": name}


@app.get("/incidents_dummy")
async def incidents_dummy(severity: str = None):
    """
    Dummy incidents endpoint — demonstrates query parameters.
    Returns mock data, optionally filtered by severity.
    Example: GET /incidents_dummy?severity=high
    """
    # Static mock data for demonstration
    all_incidents = [
        {"id": 1, "description": "Fire on Main Street",  "severity": "high", "source": "citizen"},
        {"id": 2, "description": "Minor car accident",   "severity": "low",  "source": "police"},
        {"id": 3, "description": "Medical emergency",    "severity": "high", "source": "dispatcher"},
        {"id": 4, "description": "Noise complaint",      "severity": "low",  "source": "citizen"},
    ]

    # Filter by severity if provided, otherwise return all
    if severity:
        return [i for i in all_incidents if i["severity"] == severity]
    return all_incidents