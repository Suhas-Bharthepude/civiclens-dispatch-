# Database Concepts for CivicLens Dispatch

## What is a Database?
A **database** is an organized collection of structured data that can be easily accessed, managed, and updated. Think of it as an electronic filing system.

## Key Database Concepts

### Table
A **table** is a collection of related data organized in rows and columns, like a spreadsheet.

Example: `incidents` table stores all incident reports.

### Schema
A **schema** is the structure/blueprint of a database. It defines:
- What tables exist
- What columns each table has
- Data types for each column
- Relationships between tables

### Row (Record)
A **row** (also called a record) represents a single entry in a table.

Example: One incident report = one row in the incidents table.

### Column (Field)
A **column** (also called a field) represents a specific attribute of the data.

Example: `description`, `location`, `severity` are columns in incidents table.

### Primary Key
A **primary key** is a unique identifier for each row in a table.

- Must be unique (no duplicates)
- Cannot be NULL
- Usually auto-incremented

Example: `id` column in incidents table (1, 2, 3, 4...)

### Foreign Key
A **foreign key** is a column that references the primary key of another table, creating a relationship between tables.

Example (future):
- `incidents` table has `dispatcher_id` column
- References `id` in `users` table
- Links each incident to the dispatcher who handled it

## CivicLens Database Schema

### Incidents Table

```sql
CREATE TABLE incidents (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core Fields (Required)
    source VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    
    -- Media Paths (Optional)
    audio_path VARCHAR(500),
    image_path VARCHAR(500),
    
    -- AI-Generated Fields (Optional)
    transcript TEXT,
    summary TEXT,
    risk_score REAL,
    incident_type VARCHAR(100),
    severity VARCHAR(50)
);
```

### Data Types

- **INTEGER**: Whole numbers (1, 2, 3, 100)
- **VARCHAR(n)**: Variable-length text up to n characters
- **TEXT**: Long text with no practical limit
- **REAL**: Floating-point numbers (0.5, 3.14, 0.87)

### Constraints

- **NOT NULL**: Column must have a value
- **PRIMARY KEY**: Unique identifier for rows
- **AUTOINCREMENT**: Database automatically assigns next number

## PostgreSQL vs SQLite

### SQLite (Current - Development)
- File-based database (test.db file)
- No separate server needed
- Great for development and testing
- Limited concurrent writes

### PostgreSQL (Production)
- Server-based database
- Better performance at scale
- Better concurrent access
- Industry standard for web apps

## Why We Use Both Drivers

### asyncpg (Async Operations)
```python
# For all CRUD operations in routes
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```
- Non-blocking database queries
- Better performance in async FastAPI
- Used by `databases` library

### psycopg2 (Sync Operations)
```python
# For table creation only
engine = create_engine(sync_db_url)
metadata.create_all(engine)
```
- Synchronous operations
- Used by SQLAlchemy's `create_all()` method
- Runs once at startup

## Query Examples

### INSERT (Create)
```python
query = incidents.insert().values(
    source="citizen",
    description="Fire reported",
    location="123 Main St"
)
incident_id = await database.execute(query)
```

### SELECT (Read)
```python
# Get all incidents
query = incidents.select()
results = await database.fetch_all(query)

# Get one incident
query = incidents.select().where(incidents.c.id == 5)
incident = await database.fetch_one(query)
```

### UPDATE (Modify)
```python
query = (
    incidents
    .update()
    .where(incidents.c.id == 5)
    .values(severity="high")
)
await database.execute(query)
```

### DELETE (Remove)
```python
query = incidents.delete().where(incidents.c.id == 5)
await database.execute(query)
```

## Connection String Format

```
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE
│                   │        │         │    │    │
│                   │        │         │    │    └─ Database name
│                   │        │         │    └────── Port (5432 default)
│                   │        │         └─────────── Server address
│                   │        └───────────────────── Password
│                   └────────────────────────────── Username
└────────────────────────────────────────────────── Driver (asyncpg)
```

---

*This document explains core database concepts used in CivicLens Dispatch*
EOF

echo "✅ docs/database.md created!"


# ============================================
# STEP 4: Create docs/architecture.md
# ============================================

echo "📝 Creating docs/architecture.md..."

cat > docs/architecture.md << 'EOF'
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
  - `documents/`: Other files
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
├── images/
│   └── {uuid}.jpg
└── documents/
    └── {uuid}.pdf
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

---

*Architecture last updated: Day 18*
*This is a living document - update as system evolves*