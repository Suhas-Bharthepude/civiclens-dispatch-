# CivicLens Dispatch - System Architecture

## Overview

CivicLens Dispatch is a multimodal AI-powered emergency triage system that processes citizen reports (text, audio, images) and assists dispatchers in prioritizing and routing incidents.

## High-Level Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Citizen   │────────▶│   FastAPI    │────────▶│ PostgreSQL  │
│  (Browser)  │◀────────│   Backend    │◀────────│  Database   │
└─────────────┘         └──────────────┘         └─────────────┘
                              │
                              │
                              ▼
                        ┌──────────┐
                        │ AI Models│
                        │  (Async) │
                        └──────────┘
                              │
                        ┌─────┴──────┐
                        │            │
                        ▼            ▼
                    ┌─────┐      ┌───────┐
                    │ ASR │      │Vision │
                    └─────┘      └───────┘
```

## System Components

### 1. Frontend (Future - Days 22-30)
- **Technology**: React + TypeScript
- **Purpose**: User interfaces for citizens and dispatchers
- **Components**:
  - Citizen submission form (text, audio, image)
  - Dispatcher dashboard (incident list + detail view)
  - Real-time updates (WebSockets - stretch goal)

### 2. Backend API (Current)
- **Technology**: FastAPI + Python
- **Port**: 8000 (development)
- **Responsibilities**:
  - Accept incident submissions
  - Store data in database
  - Serve incident data to frontend
  - Orchestrate AI processing pipeline
  - Handle file uploads

### 3. Database (Current)
- **Technology**: PostgreSQL (async with asyncpg)
- **Purpose**: Persistent storage
- **Tables**:
  - `incidents`: Main incident data + AI outputs
  - `users` (future): Dispatcher authentication

### 4. AI Processing Pipeline (Stub - Days 31-54)
- **Approach**: Asynchronous background processing
- **Services** (all stubs currently):
  - ASR (Automatic Speech Recognition)
  - Text Classification
  - Summarization
  - Vision Analysis
  - Risk Scoring

### 5. File Storage (Current - Local Disk)
- **Location**: `backend/app/media/tmp/`
- **Structure**:
  - `audio/`: Audio recordings
  - `images/`: Incident photos
- **Future**: S3-compatible object storage (MinIO/AWS S3)

## Data Flow: Incident Submission to Triage

### Phase 1: Submission (Synchronous)
```
1. Citizen submits incident via POST /incidents
   ├─ Text description (required)
   ├─ Location (required)
   ├─ Source (required)
   └─ Audio/Image files (optional)

2. FastAPI validates data using Pydantic schemas

3. Insert core fields into database
   └─ Returns incident_id immediately

4. Schedule background AI processing
   └─ Response sent to user (fast!)
```

### Phase 2: AI Processing (Asynchronous Background)
```
5. Background task starts (doesn't block HTTP response)

6. IF audio_path exists:
   ├─ Transcribe audio → transcript
   └─ Save transcript to database

7. Classify text (description + transcript):
   ├─ Determine incident_type
   ├─ Determine severity
   └─ Save to database

8. Generate summary:
   ├─ Combine description + transcript
   ├─ Create concise summary
   └─ Save to database

9. IF image_path exists:
   ├─ Analyze image (detect objects, hazards)
   ├─ Extract labels
   └─ Save to database

10. Calculate risk score:
    ├─ Fusion logic combines:
    │  ├─ Text severity
    │  ├─ Image labels
    │  └─ Keywords (emergency, urgent)
    └─ Save risk_score to database

11. Processing complete!
```

### Phase 3: Dispatcher View (Synchronous)
```
12. Dispatcher opens dashboard

13. Frontend fetches GET /incidents
    └─ With filters: severity, type, risk_score

14. Display sorted list:
    ├─ Highest risk_score first
    ├─ Color-coded by severity
    └─ Show AI summary

15. Dispatcher clicks incident

16. Frontend fetches GET /incidents/{id}

17. Show full details:
    ├─ Original description
    ├─ AI transcript (if audio)
    ├─ AI summary
    ├─ AI classifications
    ├─ Risk score + explanation
    └─ Media (audio player, image viewer)
```

## API Endpoints

### Core Incident Management
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| GET | `/incidents` | List incidents (with filters) |
| POST | `/incidents` | Create new incident |
| GET | `/incidents/{id}` | Get incident details |
| PATCH | `/incidents/{id}` | Update incident |
| DELETE | `/incidents/{id}` | Delete incident |

### File Uploads
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/incidents/{id}/audio` | Upload audio file |
| POST | `/incidents/{id}/image` | Upload image file |

### Processing
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/incidents/{id}/process` | Manually trigger AI processing |

## Technology Stack

### Backend
- **FastAPI**: Async web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database
- **databases**: Async database client
- **Pydantic**: Data validation
- **python-dotenv**: Environment configuration

### Database
- **PostgreSQL**: Production database
- **asyncpg**: Async PostgreSQL driver
- **psycopg2**: Sync driver (for table creation)

### AI/ML (Future)
- **Hugging Face Transformers**: Pre-trained models
- **Whisper**: ASR model
- **BLIP/CLIP**: Vision models
- **DistilBERT**: Text classification

### Storage
- **Current**: Local filesystem
- **Future**: S3-compatible (MinIO/AWS S3)

### Frontend (Future)
- **React**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **MUI/Chakra**: Component library

## File Organization

```
backend/
├── app/
│   ├── main.py              # FastAPI app + lifecycle
│   ├── config.py            # Environment configuration
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy table definitions
│   │   └── dependencies.py  # get_db() dependency
│   ├── routes/
│   │   └── incidents.py     # All incident endpoints
│   ├── schemas/
│   │   └── incident.py      # Pydantic request/response models
│   ├── services/
│   │   └── incident_processor.py  # AI pipeline orchestrator
│   ├── utils/
│   │   └── file_utils.py    # File upload helpers
│   └── media/
│       └── tmp/
│           ├── audio/       # Uploaded audio files
│           └── images/      # Uploaded image files
├── scripts/
│   └── seed_incidents.py    # Populate test data
├── tests/
│   └── test_incidents.py    # API tests
└── requirements.txt         # Python dependencies
```

## Security Considerations

### Current (Development)
- ✅ Environment variables for secrets
- ✅ CORS enabled (restricted in production)
- ✅ Input validation with Pydantic
- ⚠️ No authentication yet

### Future (Production)
- 🔒 JWT-based authentication
- 🔒 Role-based access control (dispatcher vs admin)
- 🔒 Rate limiting
- 🔒 HTTPS/TLS
- 🔒 Input sanitization
- 🔒 SQL injection prevention (automatic with SQLAlchemy)

## Storage Strategy

### Current Decision: Local Disk
**Why:**
- Simple for development
- No external dependencies
- Fast local access
- No API costs

**Location:**
```
backend/app/media/tmp/
├── audio/
│   └── {uuid}.wav
└── images/
    └── {uuid}.jpg
```

**Database Storage:**
- Store relative path: `"backend/app/media/tmp/audio/abc-123.wav"`
- Used to retrieve file later for processing/serving

### Future: S3-Compatible Storage
**When:** Day 50+ or production deployment

**Why Upgrade:**
- ✅ Scalable (unlimited storage)
- ✅ Redundancy (automatic backups)
- ✅ CDN integration (fast global access)
- ✅ No local disk space limits

**Options:**
- AWS S3 (cloud)
- MinIO (self-hosted S3-compatible)
- Cloudflare R2 (cloud, lower cost)

**Migration Plan:**
1. Install boto3/minio client
2. Add S3 credentials to .env
3. Update `file_utils.py` to use S3 SDK
4. Keep database paths as-is (just change storage backend)
5. Optional: Migrate existing files from disk to S3

## Performance Considerations

### Current Bottlenecks
1. **Sequential AI processing**: Each model runs one after another
2. **Single-threaded background tasks**: FastAPI's built-in BackgroundTasks

### Future Optimizations (Days 50+)
1. **Parallel AI processing**: Run ASR and vision analysis simultaneously
2. **Distributed task queue**: Celery + Redis for multiple workers
3. **Caching**: Redis for frequently accessed incidents
4. **Database indexing**: Speed up queries on risk_score, severity, type
5. **Connection pooling**: Reuse database connections

## Monitoring & Observability (Days 55+)

### Metrics to Track
- API request latency (per endpoint)
- AI processing time (per service)
- Error rates
- Incident volume over time
- Database query performance

### Logging Strategy
- Structured logs (JSON format)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Timestamp all log entries
- Include incident_id for traceability

## Scalability Path

### Phase 1: Single Server (Current)
- All components on one machine
- Good for development and MVP

### Phase 2: Separated Services (Future)
```
├── Web Server (FastAPI)
├── Database Server (PostgreSQL)
├── Worker Pool (Celery workers)
└── Object Storage (S3)
```

### Phase 3: Containerization (Day 68)
- Docker containers for each service
- docker-compose for local dev
- Kubernetes for production (stretch)

## AI Model Integration Strategy

### Current: Stubs
All AI services return fake/hardcoded data for testing architecture.

### Phase 1: API-Based Models (Days 31-54)
- Use hosted Hugging Face Inference API
- Pros: No local GPU needed, easy to swap models
- Cons: API costs, network latency

### Phase 2: Self-Hosted Models (Advanced)
- Run models locally with GPU
- Pros: Lower latency, no API costs
- Cons: Requires GPU, more complex deployment

## Next Steps

- [x] Day 19: Add .env configuration ✅
- [x] Day 20: Write pytest tests ✅
- [x] Day 21: Clean up and document ✅
- [ ] Days 22-30: Build React frontend
- [ ] Days 31-40: Add real AI models (ASR, summarization)
- [ ] Days 41-50: Add vision and classification models

## Recent Changes (Day 21 Review)

### What Changed Since Day 18

#### Configuration (Day 19)
- Added comprehensive environment variable management
- Created `.env.example` template
- Switched to SQLite for development (no PostgreSQL server needed)
- Fixed database.py to handle sync/async SQLite properly

#### Testing (Day 20)
- Added pytest with 19 tests
- Created test_basics.py (pytest fundamentals - 6 tests)
- Created test_api.py (endpoint tests - 5 tests)
- Created test_incidents.py (CRUD tests - 8 tests)
- Added test fixtures for database setup/teardown
- Added pytest-cov for coverage reporting

#### Code Organization (Day 21)
- Marked `app/tasks/incident_tasks.py` as deprecated
- All background processing now in `app/services/incident_processor.py`
- Test directory properly structured in `backend/tests/`
- Created comprehensive project documentation

### Current State Summary

**Working:**
- All API endpoints functional
- Database operations (CRUD)
- File uploads (audio, images)
- Background AI processing (stub)
- 19 tests passing
- Configuration management

**Ready for:**
- Frontend development (React)
- Real AI model integration (Days 31+)
- Advanced features (maps, auth, etc.)