# CivicLens Dispatch - Learning Notes (Days 1-18)

## Day 1-3: Project Setup
- **Git basics**: Learned version control with commit, push, branching
- **Virtual environments**: Isolated Python dependencies with venv
- **Project structure**: Organized folders for backend, frontend, docs

## Day 4-5: HTTP and REST
- **HTTP requests**: GET, POST, PUT, DELETE methods
- **REST concepts**: Endpoints, routes, status codes, JSON bodies
- **requests library**: Making HTTP calls from Python

## Day 6-7: FastAPI Basics
- **FastAPI app**: Created basic app with uvicorn server
- **Routes**: Defined endpoints with path and query parameters
- **Path parameters**: `/echo/{name}` - extract values from URL
- **Query parameters**: `?severity=high` - filter results

## Day 8: Pydantic Models
- **Data validation**: Automatic validation with Pydantic
- **Type hints**: Enforce data types for request/response
- **Schema separation**: IncidentCreate vs IncidentRead models

## Day 9-10: SQL and PostgreSQL
- **Relational databases**: Tables, rows, columns, relationships
- **SQL basics**: CREATE, INSERT, SELECT, UPDATE, DELETE
- **Primary keys**: Unique identifiers for each row
- **Foreign keys**: Link tables together

## Day 11-12: SQLAlchemy ORM
- **ORM concept**: Object-Relational Mapping - work with DB using Python classes
- **Engine**: Connection to database
- **Metadata**: Registry of table definitions
- **Table definitions**: Define schema with Column objects

## Day 13: Reading Data
- **SELECT queries**: Fetch data from database
- **Filtering**: WHERE clauses to narrow results
- **Pagination**: LIMIT and OFFSET for large datasets
- **Sorting**: ORDER BY for organizing results

## Day 14: Code Organization
- **Routers**: Organize endpoints by feature
- **Modular structure**: Separate concerns (routes, schemas, db, services)
- **Seed scripts**: Populate database with test data

## Day 15-16: Async Processing
- **Background tasks**: Don't block HTTP responses with slow work
- **FastAPI BackgroundTasks**: Built-in way to schedule work after response
- **Use cases**: AI processing, email sending, file processing

## Day 17: File Uploads
- **UploadFile**: FastAPI's file upload handler
- **Multipart forms**: How files are sent over HTTP
- **File storage**: Saving uploaded files to disk with unique names

## Day 18: Storage Strategy
- **Local storage**: Start with disk-based file storage
- **S3-compatible**: Plan for scalable cloud storage later
- **File paths**: Store relative paths in database, actual files on disk

## Day 19: Configuration
- **Environment variables**: Keep secrets out of code
- **.env file**: Store config locally (never commit!)
- **Config module**: Central place for all settings
- **python-dotenv**: Load .env automatically

---

## Key Takeaways So Far

✅ **FastAPI** is async-first and perfect for AI workloads
✅ **Pydantic** makes data validation automatic and type-safe
✅ **SQLAlchemy** + **databases** library = async database access
✅ **Background tasks** keep API responsive while doing heavy work
✅ **Config management** keeps secrets safe and code clean


## Next Steps (Days 19-30)

- Add real AI models (ASR, classification, summarization)
- Build React frontend
- Implement mapping/geocoding
- Add authentication
- Write comprehensive tests

---

*These notes capture my learning journey building CivicLens Dispatch*





civiclens-dispatch/
│
├── .venv/                                    # Virtual environment (do not commit)
│
├── backend/
│   ├── __init__.py
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI app entry point
│   │   ├── config.py                        # Environment configuration
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py                  # Database connection setup
│   │   │   ├── dependencies.py              # get_db() dependency
│   │   │   └── models.py                    # SQLAlchemy table definitions
│   │   │
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── incidents.py                 # All incident endpoints
│   │   │
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── incident.py                  # Pydantic models
│   │   │
│   │   ├── services/
│   │   │   └── incident_processor.py        # AI pipeline (stub)
│   │   │
│   │   ├── tasks/
│   │   │   └── incident_tasks.py            # Background task helpers
│   │   │
│   │   ├── utils/
│   │   │   └── file_utils.py                # File upload utilities
│   │   │
│   │   ├── media/
│   │   │   └── tmp/
│   │   │       ├── audio/
│   │   │       │   └── .gitkeep             # Keep folder in git
│   │   │       ├── images/
│   │   │       │   └── .gitkeep             # Keep folder in git
│   │   │       └── documents/
│   │   │           └── .gitkeep             # Keep folder in git
│   │   │
│   │   └── uploads/
│   │       └── .gitkeep                     # Alternative upload location
│   │
│   ├── playground/
│   │   ├── http_playground.py               # HTTP/JSON experiments
│   │   └── test_api.py                      # Manual API testing script
│   │
│   ├── scripts/
│   │   └── seed_incidents.py                # Database seeding script
│   │
│   ├── sql/
│   │   └── experiments.sql                  # SQL learning exercises
│   │
│   ├── tests/
│   │   └── test_incidents.py                # API tests (Day 20)
│   │
│   ├── .env                                 # Environment variables (DO NOT COMMIT)
│   ├── requirements.txt                     # Python dependencies
│   ├── test.db                              # SQLite database (dev only)
│   └── venv/                                # Alternative venv location (if used)
│
├── frontend/                                # React app (Days 22-30)
│   └── (empty for now)
│
├── infra/                                   # Docker/deployment (Day 68)
│   └── (empty for now)
│
├── docs/
│   ├── architecture.md                      # **NEW** - System architecture
│   ├── concepts.md                          # REST API concepts
│   ├── database.md                          # **NEW** - Database concepts
│   ├── pipeline.md                          # (Day 40 - future)
│   ├── performance.md                       # (Day 58 - future)
│   ├── demo_script.md                       # (Day 61 - future)
│   ├── resume_bullets.md                    # (Day 64 - future)
│   └── slides/                              # (Day 63 - future)
│
├── notes/
│   └── learning-notes.md                    # Daily learning log
│
├── .gitignore                               # Git ignore rules
├── LICENSE                                  # Project license
├── README.md                                # Project overview
└── roadmap.md                               # 75-day roadmap





## Day 19: Environment Variables & Configuration

- **Environment variables**: Store configuration separately from code
- **.env file**: Local file with KEY=VALUE pairs (never commit!)
- **os.getenv()**: Read environment variables in Python
- **python-dotenv**: Automatically load .env file on startup
- **Configuration class**: Central place for all settings
- **Default values**: Fallback if environment variable not set
- **.env.example**: Template showing what variables are needed
- **SQLite**: File-based database, perfect for development (no server needed)

### Key Takeaways

✅ Secrets belong in .env, not in code  
✅ Each environment (dev/staging/prod) has its own .env  
✅ Always provide sensible defaults for optional settings  
✅ SQLite for dev, PostgreSQL for production  

---

*Day 19 complete!*