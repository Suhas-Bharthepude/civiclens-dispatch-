# CivicLens Dispatch — System Architecture

*Last updated: Day 54*

## High-Level Overview

CivicLens Dispatch is a three-tier application with an AI processing pipeline:

```
┌─────────────────────┐
│   React Frontend    │  Port 5173
│   (Vite + React 18) │  Displays dashboard, forms, AI results
└─────────┬───────────┘
          │ HTTP/JSON
          ▼
┌─────────────────────┐
│   FastAPI Backend   │  Port 8000
│   (Python 3.13)     │  REST API, file handling, AI orchestration
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
┌────────┐  ┌──────────────────────┐
│ SQLite │  │ Hugging Face AI      │
│   DB   │  │ (4 models, 3 modals) │
└────────┘  └──────────────────────┘
```

## Component Details

### Frontend (React)
- **Framework:** React 18 with Vite build tool
- **State management:** React hooks (useState, useEffect, useMemo, useCallback)
- **API communication:** Centralized client (`api/client.js`) with shared error handling
- **Key components:**
  - `StatsBar` — Dashboard KPIs computed from incident data
  - `IncidentsList` — Table with sort, filter, search, auto-refresh
  - `IncidentDetail` — Side panel showing all AI analysis results
  - `SubmitIncidentForm` — Citizen submission form with file uploads
  - `AIStatusIndicator` — Real-time AI pipeline health badge
  - `HealthCheck` — Backend connectivity indicator

### Backend (FastAPI)
- **Framework:** FastAPI with async/await throughout
- **Database:** SQLAlchemy Core + databases library (async)
- **Validation:** Pydantic models for request/response schemas
- **Background tasks:** FastAPI BackgroundTasks for AI pipeline
- **File handling:** UUID-named files in local media directory
- **CORS:** Configured for frontend access

### Database (SQLite)
- **Table:** `incidents` with 12 columns
- **Core fields:** id, source, description, location, created_at
- **File fields:** audio_path, image_path
- **AI fields:** transcript, incident_type, severity, summary, risk_score, image_caption

### AI Pipeline
- **Orchestrator:** `incident_processor.py` coordinates all services
- **Execution:** Two-phase parallel processing with asyncio.gather()
- **Error handling:** Each service has independent try/except with fallbacks
- **Models:**

| Service | Model | Input | Output |
|---------|-------|-------|--------|
| ASR | openai/whisper-large-v3 | Audio bytes | Transcript text |
| Object Detection | facebook/detr-resnet-50 | Image bytes | Object labels |
| Classification | facebook/bart-large-mnli | Text | Type + Severity |
| Summarization | facebook/bart-large-cnn | Text | Summary |
| Risk Scoring | facebook/bart-large-mnli | Text | Score (0.0-1.0) |

## Data Flow

### Incident Submission
```
1. Citizen fills form → POST /incidents → incident created (ID returned)
2. Audio uploaded → POST /incidents/{id}/audio → file saved to disk
3. Image uploaded → POST /incidents/{id}/image → file saved to disk
4. Background task queued → process_incident(id) starts asynchronously
5. Response returned immediately (user doesn't wait for AI)
```

### AI Processing (Background)
```
Phase 1 — Media Processing (parallel):
  ├─ ASR: audio file → Whisper API → transcript text
  └─ Vision: image file → DETR API → object labels

Phase 2 — Text Analysis (parallel, needs Phase 1 output):
  ├─ Classification: combined text → BART-MNLI → type + severity
  ├─ Summarization: combined text → BART-CNN → summary
  └─ Risk Scoring: combined text → BART-MNLI → risk score

All results saved to database in single UPDATE query
```

### Dispatcher View
```
1. Dashboard auto-refreshes every 30 seconds
2. New incidents appear in table with AI results
3. Click incident → detail panel shows all AI fields
4. Filter by type/severity, search by keyword, sort by any column
5. Reprocess button re-runs AI if initial processing failed
```

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | /health | Server health |
| GET | /ai/status | AI model health (parallel checks) |
| POST | /incidents | Create incident |
| GET | /incidents | List (with filter/search) |
| GET | /incidents/{id} | Get one |
| PATCH | /incidents/{id} | Update |
| DELETE | /incidents/{id} | Delete |
| POST | /incidents/{id}/audio | Upload audio |
| POST | /incidents/{id}/image | Upload image |
| POST | /incidents/{id}/reprocess | Re-run AI pipeline |

## Performance

- **Pipeline time:** ~20-45s parallel vs ~60-120s sequential
- **AI status check:** ~0.5s (all 4 models checked in parallel)
- **API response:** <50ms for CRUD operations
- **Auto-refresh:** 30s for incidents, 60s for AI status

## Security Considerations

**Current (Development):**
- Environment variables for API keys
- CORS configured (allows all origins in dev)
- Pydantic input validation
- No authentication (development only)

**Production would need:**
- JWT authentication
- Role-based access (dispatcher vs admin)
- HTTPS/TLS
- Rate limiting
- Restricted CORS origins
- Input sanitization

## Future Enhancements

- WebSocket real-time updates (replace polling)
- PostgreSQL for production
- Docker containerization
- Celery + Redis for distributed task queue
- Map visualization for incident locations
- User authentication and role management



## Configuration Architecture (Day 67)

### How Config Works

All application settings live in `backend/app/config.py`. No other file reads directly from environment variables — everything goes through the `settings` object.

```
.env file  ──→  config.py Settings class  ──→  rest of the app
                    ↓
            environment-aware properties
            (effective_debug, effective_cors_origins, etc.)
```

### Environment Variable → Behavior Map

| Variable | Development | Production |
|---|---|---|
| `ENVIRONMENT` | `development` | `production` |
| `DEBUG` | `true` | `false` (forced) |
| `LOG_LEVEL` | `INFO` | `WARNING` (forced) |
| `CORS_ORIGINS` | `*` (forced) | Your frontend URL |
| `DATABASE_URL` | SQLite | PostgreSQL |
| `HUGGINGFACE_API_KEY` | Your token | Your token |

### Switching Environments

**Development (local):**
```bash
# backend/.env
ENVIRONMENT=development
DATABASE_URL=sqlite+aiosqlite:///./test.db
```

**Production (server):**
```bash
# Set in Render / Railway / Heroku dashboard — never in a committed file
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
CORS_ORIGINS=https://your-app.vercel.app
```

No code changes between environments — only environment variables change.

### Files

| File | Purpose | Committed? |
|---|---|---|
| `backend/.env` | Your real local config with secrets | ❌ No (.gitignore) |
| `backend/.env.example` | Template showing what variables are needed | ✅ Yes |
| `backend/app/config.py` | Settings class + environment-aware properties | ✅ Yes |