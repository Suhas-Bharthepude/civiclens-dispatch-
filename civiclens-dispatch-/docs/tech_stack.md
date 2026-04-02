# Tech Stack — CivicLens Dispatch

## Backend

| Technology | Version | Purpose |
|-----------|---------|---------|
| Python | 3.13 | Primary programming language |
| FastAPI | latest | Async web framework with auto-generated API docs |
| SQLAlchemy | latest | SQL toolkit and ORM for database operations |
| databases | latest | Async database access (works with SQLAlchemy) |
| aiosqlite | latest | Async SQLite driver for development |
| Pydantic | v2 | Data validation, serialization, settings management |
| httpx | latest | Async HTTP client for calling Hugging Face APIs |
| python-dotenv | latest | Load environment variables from .env files |
| uvicorn | latest | ASGI server to run FastAPI |

## Frontend

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 18 | Component-based UI framework |
| Vite | latest | Fast build tool and development server |
| CSS | — | Custom styling (no CSS framework) |
| JavaScript (ES6+) | — | Frontend logic with modern syntax |

## AI Models (Hugging Face Inference API)

| Model | Provider | Task | Why This Model |
|-------|----------|------|---------------|
| openai/whisper-large-v3 | OpenAI | Speech-to-text | Best open-source ASR, 99 languages |
| facebook/bart-large-mnli | Meta | Zero-shot classification | Classifies text into any categories without training |
| facebook/bart-large-cnn | Meta | Abstractive summarization | Trained on news articles, great for incident reports |
| facebook/detr-resnet-50 | Meta | Object detection | Identifies 80+ object types in images |

## Database

| Technology | Environment | Purpose |
|-----------|------------|---------|
| SQLite | Development | File-based database, zero setup |
| PostgreSQL | Production (planned) | Scalable, concurrent access |

## Development Tools

| Tool | Purpose |
|------|---------|
| Git | Version control |
| GitHub | Code hosting and collaboration |
| pytest | Python testing framework |
| npm | JavaScript package manager |

## Key Design Decisions

**Why FastAPI over Flask/Django?**
Native async support, automatic API docs, Pydantic integration, modern Python features.

**Why React over Vue/Angular?**
Most in-demand framework, huge ecosystem, component model fits dashboard architecture.

**Why Hugging Face API over local models?**
No GPU required, zero infrastructure, free tier available, easy model swapping.

**Why zero-shot classification over trained models?**
No labeled training data needed, works immediately with any categories, easy to adjust.

**Why SQLite over PostgreSQL for development?**
Zero setup, file-based, perfect for development. Architecture supports PostgreSQL swap for production.