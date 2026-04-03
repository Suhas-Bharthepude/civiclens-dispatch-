# CivicLens Dispatch 🚨

> AI-powered emergency incident triage system — automatically classifies, prioritizes, and summarizes citizen-reported incidents so dispatchers can focus on what matters most.

---

## Screenshots

![Dashboard showing incidents sorted by risk score](docs/screenshots/dashboard.png)
*Dispatcher dashboard — incidents pre-sorted by AI-generated risk score. Highest urgency at the top.*

![Detail panel showing AI-generated fields](docs/screenshots/detail_panel.png)
*Incident detail panel — shows AI classification, risk score, summary, and transcript side by side.*

![Citizen submission form](docs/screenshots/submit_form.png)
*Citizen submission form — accepts text description, location, optional audio and image uploads.*

![AI fields on incident row](docs/screenshots/ai_fields.png)
*AI pipeline output — incident type, severity badge, and risk score populated automatically within seconds.*

---

## What It Does

Emergency dispatch centers receive hundreds of unstructured reports every day — text messages, voice calls, photos — from citizens, sensors, and field units. Dispatchers manually read each one, figure out what type of incident it is, how urgent it is, and write a summary. This is slow and error-prone under pressure.

**CivicLens Dispatch automates that triage pipeline using multimodal AI:**

1. A citizen submits an incident report (text, audio, or photo)
2. The system automatically transcribes audio, analyzes images, classifies the incident type, scores urgency, and generates a summary
3. Dispatchers see a pre-sorted, pre-analyzed feed — highest risk incidents at the top

**The result:** Dispatchers spend less time reading raw reports and more time making decisions.

---

## Live Demo

> *Demo video coming Day 63*

**What the AI pipeline produces from a single text report:**

```
Input:  "Major fire at warehouse on Industrial Blvd. Thick black smoke.
         Two workers trapped on second floor. Explosions heard."

Output:
  Type:     fire
  Severity: high
  Risk:     75% (0.7533)
  Summary:  "At least two workers reported trapped on the second floor.
             Explosions heard from inside. Area being evacuated."
  Time:     5.1 seconds
```

---

## Architecture

```
Citizen Report (text / audio / image)
         │
         ▼
   FastAPI Backend  ←──── Async REST API
         │
         ▼
  Background Pipeline (asyncio)
    ├── Phase 1 (parallel)
    │     ├── ASR: openai/whisper-base       (audio → text)
    │     └── Vision: facebook/detr-resnet-50 (image → caption)
    │
    └── Phase 2 (parallel, after Phase 1)
          ├── Classifier: facebook/bart-large-mnli  (type + severity)
          ├── Summarizer: facebook/bart-large-cnn   (summary)
          └── Risk Scorer: facebook/bart-large-mnli (urgency 0–1)
         │
         ▼
    SQLite Database  (incidents + all AI fields)
         │
         ▼
    React Dashboard  (live feed, filters, search, detail panel)
```

**Why two parallel phases?**
Phase 2 needs the transcript from Phase 1 (ASR must finish before we can classify enriched text). Within each phase, tasks are independent and run simultaneously with `asyncio.gather()`. This cuts pipeline time significantly compared to sequential processing.

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Backend | FastAPI (Python) | Async-native, automatic API docs, fast |
| Database | SQLite → PostgreSQL | Simple dev, production-ready upgrade path |
| ORM | SQLAlchemy + `databases` | Async queries, clean table definitions |
| AI Models | Hugging Face Inference API | No GPU required, 4 models, free tier |
| Frontend | React 18 | Component model, state management |
| Testing | pytest + httpx | Async test support, full coverage |
| Validation | Pydantic | Schema validation, clear error messages |

---

## AI Models

| Model | Task | Output |
|---|---|---|
| `openai/whisper-base` | Audio transcription (ASR) | Text transcript from voice reports |
| `facebook/detr-resnet-50` | Object detection | Scene description from photos |
| `facebook/bart-large-mnli` | Zero-shot classification | Incident type + severity label |
| `facebook/bart-large-mnli` | Zero-shot risk scoring | Urgency score 0.0–1.0 |
| `facebook/bart-large-cnn` | Summarization | 1–2 sentence dispatcher summary |

**Zero-shot classification** means the models were never specifically trained on emergency dispatch data — they understand language well enough to classify incident types and severity from natural language descriptions without task-specific training data.

---

## API Endpoints

```
GET    /health                      Health check
GET    /ai/status                   AI pipeline model status

POST   /incidents                   Create incident (triggers AI pipeline)
GET    /incidents                   List incidents (filter, search, sort)
GET    /incidents/stats             Analytics summary
GET    /incidents/{id}              Get single incident
PATCH  /incidents/{id}              Update incident
DELETE /incidents/{id}              Delete incident
POST   /incidents/{id}/audio        Upload audio file
POST   /incidents/{id}/image        Upload image file
POST   /incidents/{id}/reprocess    Re-run AI pipeline
```

**Filtering and search:**
```
GET /incidents?severity=high
GET /incidents?type=fire
GET /incidents?search=warehouse
GET /incidents?sort_by=risk_score&sort_dir=desc
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- A free [Hugging Face account](https://huggingface.co) for the API token

### Backend Setup

```bash
# Clone the repo
git clone https://github.com/Suhas-Bharthepude/civiclens-dispatch-.git
cd civiclens-dispatch-

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env — add your HUGGINGFACE_API_TOKEN

# Start the server
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000`
Auto-generated docs at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Dashboard runs at `http://localhost:5173`

---

## Running Tests

```bash
cd backend

# Full test suite
PYTHONPATH=. python scripts/test_e2e.py       # 6/6 end-to-end tests
PYTHONPATH=. python scripts/test_errors.py    # 14/14 error handling tests
PYTHONPATH=. python scripts/test_performance.py  # Query performance benchmarks
```

**Test results (Day 60):**
- ✅ 6/6 E2E tests passing (health, AI status, create, pipeline, reprocess, search)
- ✅ 14/14 error handling tests (empty body, invalid source, missing fields, 404s, type errors)
- ✅ AI pipeline completes in ~5s per incident
- ✅ Database queries under 10ms with indexes on type, severity, risk_score, created_at

---

## Project Structure

```
civiclens-dispatch-/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + startup/shutdown
│   │   ├── config.py                  # Environment config
│   │   ├── db/
│   │   │   ├── database.py            # Async DB connection
│   │   │   └── models.py              # SQLAlchemy table definitions
│   │   ├── routes/
│   │   │   ├── incidents.py           # All /incidents endpoints
│   │   │   └── ai_status.py           # /ai/status endpoint
│   │   ├── schemas/
│   │   │   └── incident.py            # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── incident_processor.py  # Main AI pipeline orchestrator
│   │   │   ├── asr.py                 # Audio transcription (Whisper)
│   │   │   ├── image_analyzer.py      # Image analysis (DETR)
│   │   │   ├── text_classifier.py     # Type + severity (BART-MNLI)
│   │   │   ├── summarizer.py          # Summary (BART-CNN)
│   │   │   └── risk_scorer.py         # Urgency score (BART-MNLI)
│   │   ├── validators.py              # Business rule validation
│   │   └── utils/
│   │       └── file_utils.py          # File upload helpers
│   └── scripts/
│       ├── test_e2e.py                # End-to-end integration tests
│       ├── test_errors.py             # Error handling tests
│       ├── test_performance.py        # Query performance tests
│       └── seed_incidents.py          # Seed database with test data
├── frontend/
│   └── src/
│       ├── components/
│       │   └── dashboard/             # Dashboard UI components
│       └── App.jsx
├── docs/
│   ├── demo_script.md                 # Live demo walkthrough
│   ├── architecture.md                # System design decisions
│   └── pipeline.md                    # AI pipeline documentation
└── roadmap.md                         # 75-day build plan
```

---

## What I Learned

This project was built over 61 days as a structured learning journey. Key concepts covered:

- **Async Python** — `async/await`, `asyncio.gather()` for parallel AI calls
- **REST API design** — resource modeling, status codes, error schemas
- **Database** — SQLAlchemy ORM, async queries, indexing for performance
- **AI integration** — Hugging Face Inference API, zero-shot classification, ASR, vision models
- **Background tasks** — FastAPI `BackgroundTasks`, non-blocking AI processing
- **Testing** — end-to-end integration tests, error handling tests, performance benchmarks
- **Full-stack** — React frontend consuming a FastAPI backend

---

## Roadmap

- [x] **Days 1–7**: Python, FastAPI basics, Git
- [x] **Days 8–14**: Database design, SQLAlchemy, CRUD
- [x] **Days 15–21**: Async processing, file uploads, testing
- [x] **Days 22–30**: React frontend, dashboard UI
- [x] **Days 31–40**: Audio pipeline (Whisper ASR)
- [x] **Days 41–50**: Vision models, text classification, parallel pipeline
- [x] **Days 51–60**: Frontend polish, analytics, full test suite
- [ ] **Days 61–75**: Demo video, deployment, portfolio polish

---

## Author

**Suhas Bharthepude**
- GitHub: [@Suhas-Bharthepude](https://github.com/Suhas-Bharthepude)

---

*Built in 75 days as a structured full-stack + AI learning project.*