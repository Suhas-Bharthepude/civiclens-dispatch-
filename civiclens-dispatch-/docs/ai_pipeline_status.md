# AI Pipeline Status & Reprocessing - CivicLens Dispatch

## Overview

Day 50 adds two operational features: a health check endpoint for all AI models, and a reprocess endpoint to re-run AI on existing incidents.

## GET /ai/status — Pipeline Health Check

Checks whether each AI model used in the pipeline is reachable and responsive.

### Example Response

```json
{
    "pipeline_status": "healthy",
    "models_ready": 4,
    "models_total": 4,
    "models": [
        {
            "model": "openai/whisper-base",
            "task": "Audio Transcription (ASR)",
            "status": "ready",
            "response_time_seconds": 1.2,
            "detail": "Model endpoint is responding"
        },
        {
            "model": "facebook/bart-large-mnli",
            "task": "Text Classification + Risk Scoring",
            "status": "ready",
            "response_time_seconds": 0.8,
            "detail": "Model is loaded and responding"
        },
        {
            "model": "facebook/bart-large-cnn",
            "task": "Summarization",
            "status": "loading",
            "response_time_seconds": 2.1,
            "detail": "Model is loading — will be ready soon"
        },
        {
            "model": "facebook/detr-resnet-50",
            "task": "Image Analysis (Object Detection)",
            "status": "ready",
            "response_time_seconds": 0.9,
            "detail": "Model endpoint is responding"
        }
    ],
    "total_check_time_seconds": 2.3
}
```

### Pipeline Status Values

- **healthy**: All models are ready
- **degraded**: Some models are ready, some are not (partial functionality)
- **down**: No models are responding

### Individual Model Status Values

- **ready**: Model is loaded and can process requests
- **loading**: Model is loading (503 response — common on free tier after inactivity)
- **timeout**: Model didn't respond within 10 seconds
- **unreachable**: Can't connect to Hugging Face API
- **auth_error**: API key is invalid
- **error**: Other error

### How Health Checks Work

All four models are checked in parallel using `asyncio.gather()`. The total check time is the time of the slowest model, not the sum. A 400 response to our test payload is treated as "ready" because it means the endpoint exists and is processing requests — our test payload is intentionally minimal and expected to be rejected.

## POST /incidents/{id}/reprocess — Re-run AI Pipeline

Re-runs the full AI pipeline on an existing incident. Useful when:
- Original processing failed due to API timeout or rate limiting
- Incident description was updated and needs re-analysis
- You want fresh results after AI models were updated

### Example

```bash
curl -X POST http://localhost:8000/incidents/5/reprocess
```

### Response

```json
{
    "message": "Reprocessing queued for incident 5",
    "incident_id": 5,
    "status": "queued",
    "note": "AI pipeline will run in the background. Refresh to see updated results."
}
```

The pipeline runs in the background — the endpoint returns immediately. The dispatcher refreshes the page to see updated AI results.

## Complete API Endpoint Summary (Day 50)

### Core
- `GET /health` — Server health check
- `GET /` — API info

### Incidents
- `POST /incidents` — Create incident (triggers AI pipeline)
- `GET /incidents` — List incidents (with filters and search)
- `GET /incidents/{id}` — Get specific incident
- `PATCH /incidents/{id}` — Update incident
- `DELETE /incidents/{id}` — Delete incident
- `POST /incidents/{id}/audio` — Upload audio file
- `POST /incidents/{id}/image` — Upload image file
- `POST /incidents/{id}/reprocess` — Re-run AI pipeline

### AI
- `GET /ai/status` — Check all AI model health

---

*Implemented Day 50 | Milestone: Days 41-50 complete*