# backend/app/main.py
# This is the main entry point for the FastAPI application
# It creates the app, registers routes, and manages database lifecycle

# Import FastAPI core components
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import database tools
from app.db.database import database, engine, metadata
from app.db.models import incidents  # Import table so it's registered with metadata

# Import configuration settings
from app.config import settings

# Import routers (route handlers organized by feature)
from app.routes.incidents import router as incidents_router

# Import file utilities
from app.utils.file_utils import ensure_upload_dirs


# ========================================
# CREATE DATABASE TABLES
# ========================================
# This runs once when the module is imported
# Creates all tables defined in metadata if they don't exist
# This is a sync operation, so it uses the sync engine
metadata.create_all(engine)


# ========================================
# CREATE FASTAPI APPLICATION
# ========================================
app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.VERSION,
    debug=settings.DEBUG
)


# ========================================
# CONFIGURE CORS (for frontend)
# ========================================
# Allows frontend (React) to call this API from different origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========================================
# REGISTER ROUTERS
# ========================================
# Include all route modules
# Each router handles a specific feature (incidents, users, etc.)
app.include_router(
    incidents_router,
    prefix="",  # No prefix - routes already include /incidents
    tags=["incidents"]
)


# ========================================
# APPLICATION LIFECYCLE EVENTS
# ========================================

@app.on_event("startup")
async def startup_event():
    """
    Runs once when the application starts.
    Connects to the database and ensures upload directories exist.
    """
    # Connect to the database
    await database.connect()
    print(f"✅ Database connected: {settings.DATABASE_URL}")
    
    # Ensure media upload directories exist
    ensure_upload_dirs()
    
    print(f"✅ {settings.APP_TITLE} v{settings.VERSION} started")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs once when the application shuts down.
    Disconnects from the database.
    """
    # Disconnect from the database
    await database.disconnect()
    print("❌ Database disconnected")
    print("❌ Application shut down")


# ========================================
# ROOT ENDPOINTS (Day 6 & 7 Requirements)
# ========================================

@app.get("/")
async def root():
    """
    Root endpoint - basic welcome message.
    Confirms API is accessible.
    """
    return {
        "message": "CivicLens Dispatch API is running",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint (Day 6 requirement).
    Used by monitoring tools and load balancers.
    Returns 200 OK if service is healthy.
    """
    return {
        "status": "ok",
        "service": settings.APP_TITLE,
        "version": settings.VERSION
    }

@app.get("/health/pipeline")
async def pipeline_health():
    from app.services.asr import USE_MOCK_TRANSCRIPTION
    from app.services.summarization import USE_MOCK_SUMMARIZATION
    from app.services.classification import USE_MOCK_CLASSIFICATION
    from app.services.image_analysis import USE_MOCK_IMAGE_ANALYSIS
    from datetime import datetime
    from sqlalchemy import func, select as sa_select
    services = {
        "asr":            {"status": "mock" if USE_MOCK_TRANSCRIPTION else "ok",  "model": "openai/whisper-small"},
        "classification": {"status": "mock" if USE_MOCK_CLASSIFICATION else "ok", "model": "facebook/bart-large-mnli"},
        "summarization":  {"status": "mock" if USE_MOCK_SUMMARIZATION else "ok",  "model": "facebook/bart-large-cnn"},
        "image_analysis": {"status": "mock" if USE_MOCK_IMAGE_ANALYSIS else "ok", "model": "Salesforce/blip-image-captioning-base"},
    }
    try:
        count = await database.fetch_val(sa_select(func.count()).select_from(incidents))
        db = {"status": "ok", "incident_count": count}
    except Exception as e:
        db = {"status": "error", "incident_count": None}
    statuses = [s["status"] for s in services.values()]
    overall = "error" if "error" in statuses else "degraded" if "mock" in statuses else "healthy"
    return {"status": overall, "checked_at": datetime.utcnow().isoformat(), "services": services, "database": db}

@app.get("/echo/{name}")
async def echo_name(name: str):
    """
    Echo endpoint (Day 7 requirement).
    Demonstrates path parameters.
    Returns the provided name in a JSON response.
    
    Example: GET /echo/Alice → {"hello": "Alice"}
    """
    return {"hello": name}


@app.get("/incidents_dummy")
async def incidents_dummy(severity: str = None):
    """
    Dummy incidents endpoint (Day 7 requirement).
    Demonstrates query parameters and filtering.
    Returns mock incident data.
    
    Example: GET /incidents_dummy?severity=high
    """
    # Mock incident data
    all_incidents = [
        {
            "id": 1,
            "description": "Fire on Main Street",
            "severity": "high",
            "source": "citizen"
        },
        {
            "id": 2,
            "description": "Minor car accident",
            "severity": "low",
            "source": "police"
        },
        {
            "id": 3,
            "description": "Medical emergency",
            "severity": "high",
            "source": "dispatcher"
        },
        {
            "id": 4,
            "description": "Noise complaint",
            "severity": "low",
            "source": "citizen"
        }
    ]
    
    # Filter by severity if provided
    if severity:
        filtered = [
            incident for incident in all_incidents
            if incident["severity"] == severity
        ]
        return filtered
    
    # Return all if no filter
    return all_incidents


# ========================================
# RUN INSTRUCTIONS
# ========================================
# To run this application:
# 1. Activate virtual environment: source .venv/bin/activate (Linux/Mac)
#                                or .venv\Scripts\activate (Windows)
# 2. Run: uvicorn app.main:app --reload
# 3. Visit: http://127.0.0.1:8000/docs for interactive API docs