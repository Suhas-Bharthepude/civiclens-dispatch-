# backend/app/routes/ai_status.py
# AI Pipeline Status endpoint
# Reports the health and availability of all AI models used in the pipeline
#
# Endpoint: GET /ai/status
# Returns the status of each Hugging Face model (reachable or not)
#
# This is used for:
#   - Monitoring: Is the AI pipeline healthy?
#   - Debugging: Which model is down when processing fails?
#   - Dashboard: Show AI status to dispatchers
#
# Day 50: AI pipeline consolidation

# Import APIRouter from FastAPI to create a router for these endpoints
# A router groups related endpoints together (like a mini-app)
from fastapi import APIRouter

# Import httpx for making async HTTP requests to check model health
import httpx

# Import asyncio for running health checks in parallel
import asyncio

# Import time for measuring response times
import time

# Import settings for the Hugging Face API key
from app.config import settings


# ========================================
# ROUTER SETUP
# ========================================

# Create a router with the /ai prefix and "AI Status" tag
# prefix="/ai" means all routes in this file start with /ai
# tags=["AI Status"] groups these endpoints in the API docs
router = APIRouter(
    prefix="/ai",
    tags=["AI Status"],
)


# ========================================
# MODEL CONFIGURATION
# ========================================

# List of all AI models used in the pipeline
# Each entry has the model name, its URL, the task it performs,
# and what type of health check to run (text or image)
AI_MODELS = [
    {
        "name": "openai/whisper-large-v3-turbo",
        "url": "https://router.huggingface.co/hf-inference/models/openai/whisper-large-v3-turbo",
        "task": "Audio Transcription (ASR)",
        "check_type": "audio",
    },
    {
        "name": "facebook/bart-large-mnli",
        "url": "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli",
        "task": "Text Classification + Risk Scoring",
        "check_type": "text",
    },
    {
        "name": "facebook/bart-large-cnn",
        "url": "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn",
        "task": "Summarization",
        "check_type": "text",
    },
    {
        "name": "facebook/detr-resnet-50",
        "url": "https://router.huggingface.co/hf-inference/models/facebook/detr-resnet-50",
        "task": "Image Analysis (Object Detection)",
        "check_type": "image",
    },
]

# HF serverless models (especially bart-large-mnli) routinely take 10-15s
# to respond when cold. 30s matches real classification timeout well enough
# to avoid false "degraded" reports on a working pipeline.
HEALTH_CHECK_TIMEOUT = 30


# ========================================
# HEALTH CHECK HELPER
# ========================================

async def _check_model_health(model: dict) -> dict:
    """
    Check if a single AI model is reachable and responsive.
    
    We send a minimal request to the model's API endpoint and check
    if we get any response (even an error response means the model is reachable).
    
    A 200 means the model is ready.
    A 503 means the model is loading (reachable but not ready).
    A 401 means auth issue (our problem, not the model's).
    A timeout means the model is unreachable.
    
    Args:
        model: Dict with name, url, task, and check_type
    
    Returns:
        Dict with model name, task, status, response_time, and details
    """
    
    # Record the start time
    start = time.perf_counter()
    
    # Build the request headers
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
    }
    
    try:
        # Create an async HTTP client with a short timeout
        async with httpx.AsyncClient(timeout=HEALTH_CHECK_TIMEOUT) as client:
            
            # Send a minimal request based on the model type
            if model["check_type"] == "text":
                # For text models, send a tiny text payload
                headers["Content-Type"] = "application/json"
                response = await client.post(
                    model["url"],
                    headers=headers,
                    json={"inputs": "test", "parameters": {"candidate_labels": ["test"]}},
                )
            elif model["check_type"] == "audio":
                # For audio models, we just check if the endpoint responds
                # Sending empty bytes will get an error, but proves the endpoint exists
                headers["Content-Type"] = "audio/wav"
                response = await client.post(
                    model["url"],
                    headers=headers,
                    content=b"test",
                )
            elif model["check_type"] == "image":
                # For image models, send minimal bytes
                headers["Content-Type"] = "image/jpeg"
                response = await client.post(
                    model["url"],
                    headers=headers,
                    content=b"test",
                )
            else:
                # Unknown check type
                response = await client.get(model["url"], headers=headers)
        
        # Calculate response time
        elapsed = time.perf_counter() - start
        
        # Determine status based on HTTP response code
        if response.status_code == 200:
            status = "ready"
            detail = "Model is loaded and responding"
        elif response.status_code == 503:
            status = "loading"
            detail = "Model is loading — will be ready soon"
        elif response.status_code == 401:
            status = "auth_error"
            detail = "API key is invalid or missing"
        elif response.status_code == 400:
            # 400 means the endpoint exists and processed our request
            # but our test payload was invalid (expected for health checks)
            status = "ready"
            detail = "Model endpoint is responding (test payload rejected as expected)"
        else:
            status = "error"
            detail = f"HTTP {response.status_code}"
        
        return {
            "model": model["name"],
            "task": model["task"],
            "status": status,
            "response_time_seconds": round(elapsed, 2),
            "detail": detail,
        }
    
    except httpx.TimeoutException:
        # Model didn't respond within the timeout
        elapsed = time.perf_counter() - start
        return {
            "model": model["name"],
            "task": model["task"],
            "status": "timeout",
            "response_time_seconds": round(elapsed, 2),
            "detail": f"No response within {HEALTH_CHECK_TIMEOUT}s",
        }
    
    except httpx.ConnectError:
        # Can't reach the API at all
        elapsed = time.perf_counter() - start
        return {
            "model": model["name"],
            "task": model["task"],
            "status": "unreachable",
            "response_time_seconds": round(elapsed, 2),
            "detail": "Cannot connect to Hugging Face API",
        }
    
    except Exception as e:
        # Any other error
        elapsed = time.perf_counter() - start
        return {
            "model": model["name"],
            "task": model["task"],
            "status": "error",
            "response_time_seconds": round(elapsed, 2),
            "detail": str(e)[:100],
        }


# ========================================
# AI STATUS ENDPOINT
# ========================================

@router.get("/status")
async def get_ai_status():
    """
    Check the health of all AI models in the pipeline.
    
    Returns:
        JSON with:
        - pipeline_status: "healthy", "degraded", or "down"
        - models: List of individual model statuses
        - total_check_time: How long all checks took (parallel)
    
    Example response:
    {
        "pipeline_status": "healthy",
        "models_ready": 4,
        "models_total": 4,
        "models": [
            {"model": "openai/whisper-base", "status": "ready", ...},
            {"model": "facebook/bart-large-mnli", "status": "ready", ...},
            ...
        ],
        "total_check_time_seconds": 2.3
    }
    """
    
    # Record start time for the entire health check
    start = time.perf_counter()
    
    # Run ALL model health checks in parallel using asyncio.gather()
    # This checks all 4 models at the same time instead of one by one
    model_statuses = await asyncio.gather(
        *[_check_model_health(model) for model in AI_MODELS]
    )
    
    # Calculate total check time
    total_time = time.perf_counter() - start
    
    # Count how many models are ready
    ready_count = sum(
        1 for m in model_statuses
        if m["status"] in ("ready",)
    )
    total_count = len(model_statuses)
    
    # Determine overall pipeline status
    if ready_count == total_count:
        # All models are ready
        pipeline_status = "healthy"
    elif ready_count > 0:
        # Some models are ready, some are not
        pipeline_status = "degraded"
    else:
        # No models are ready
        pipeline_status = "down"
    
    # Return the complete status report
    return {
        "pipeline_status": pipeline_status,
        "models_ready": ready_count,
        "models_total": total_count,
        "models": model_statuses,
        "total_check_time_seconds": round(total_time, 2),
    }