# CivicLens Dispatch

> Multimodal AI triage for emergency dispatch centers. Turns unstructured citizen reports (text, audio, image) into structured incident records with type, severity, and risk score — in about 5 seconds.

---

## Live Demo

**Try it now:** [https://civiclens-dispatch.vercel.app](https://civiclens-dispatch.vercel.app)

**Demo credentials:**
| Username | Password |
|----------|----------|
| `dispatcher` | `dispatch123` |

> First load may take 30–60 seconds — the backend runs on Render's free tier and wakes from sleep on the first request. UptimeRobot pings every 5 minutes to keep it warm during active use.

**Backend API:** [https://civiclens-backend-d231.onrender.com](https://civiclens-backend-d231.onrender.com)

**Source:** [GitHub repository](https://github.com/Suhas-Bharthepude/civiclens-dispatch-)

---

## The Problem

Emergency dispatch centers receive a flood of unstructured reports — text messages, voice recordings, photos — from citizens, sensors, and field units. Each report must be read, classified by incident type, scored for urgency, and summarized before a dispatcher can act. That process is manual, slow, and error-prone under pressure.

CivicLens Dispatch automates the triage pipeline using multimodal AI.

---

## What the AI Produces

For every incoming report, the pipeline produces:

- **Incident type** — fire, medical, traffic, crime, infrastructure, noise, security (zero-shot classification)
- **Severity** — low, medium, high (zero-shot classification)
- **Risk score** — a 0.0–1.0 numeric urgency score
- **One-sentence summary** — generated for dispatcher scanning
- **Audio transcript** — if audio was attached (Whisper ASR)
- **Image description** — if an image was attached (DETR object detection)

Processing happens asynchronously in the background — the submission API responds in milliseconds.

---

## Architecture

```
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   Frontend   │───────▶│   Backend    │───────▶│   Database   │
│ React/Vite   │  REST  │   FastAPI    │  async │  PostgreSQL  │
│   Vercel     │  Poll  │   Render     │  ORM   │   Supabase   │
└──────────────┘        └──────┬───────┘        └──────────────┘
                               │
                               │ async HTTP
                               ▼
                     ┌──────────────────┐
                     │  Hugging Face    │
                     │  Inference API   │
                     │  (BART/Whisper/  │
                     │   DETR models)   │
                     └──────────────────┘
```

---

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Frontend | React 18 + Vite | Fast dev server, small production bundle |
| Charts | Recharts | Composable chart components |
| State/data | Custom hooks + fetch | No Redux needed at this scale |
| Realtime | Polling (WebSocket fallback) | Reliable across free-tier hosting |
| Backend | FastAPI (Python 3.11.9) | Async-native, auto-generated OpenAPI docs |
| Database | PostgreSQL via Supabase | Relational fit for incidents + users |
| ORM | SQLAlchemy + databases | Async queries with sync table creation |
| Auth | JWT with `python-jose` + bcrypt | Stateless, role-based (admin/dispatcher) |
| AI | Hugging Face Inference API | Zero-shot, ASR, vision — no self-hosting |
| Hosting | Vercel + Render + Supabase | All free-tier |
| Monitoring | UptimeRobot | Keeps Render backend awake with 5-min pings |

---

## Key API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| `POST` | `/auth/login` | Exchange credentials for JWT |
| `GET` | `/auth/me` | Get current user profile |
| `POST` | `/incidents` | Submit a new incident |
| `GET` | `/incidents` | List incidents (filter by severity/type/search) |
| `GET` | `/incidents/{id}` | Fetch a single enriched incident |
| `PATCH` | `/incidents/{id}` | Update incident status |
| `DELETE` | `/incidents/{id}` | Delete incident |
| `POST` | `/incidents/{id}/reprocess` | Re-run AI pipeline |
| `POST` | `/incidents/{id}/audio` | Upload audio file |
| `POST` | `/incidents/{id}/image` | Upload image file |
| `GET` | `/incidents/analytics/summary` | KPI counts, averages, by-type/severity |
| `GET` | `/incidents/analytics/timeseries` | Daily incident counts (zero-filled) |
| `GET` | `/incidents/analytics/risk-distribution` | Risk score histogram |
| `GET` | `/ai/status` | Health of all 4 AI models |
| `GET` | `/health` | Server liveness check |
| `WS` | `/ws/incidents` | Live push for new incidents |

---

## Local Setup

```bash
# Clone
git clone https://github.com/Suhas-Bharthepude/civiclens-dispatch-
cd civiclens-dispatch-/civiclens-dispatch-

# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Fill in: DATABASE_URL, HUGGINGFACE_API_KEY, SECRET_KEY, CORS_ORIGINS
uvicorn app.main:app --reload

# Frontend (in another terminal)
cd frontend
npm install
# Create .env with: VITE_API_URL=http://localhost:8000
npm run dev
```

For local development, the backend uses SQLite (`civiclens.db`) by default. Set `DATABASE_URL` to a PostgreSQL URL for production.

To seed users locally:
```bash
cd backend
PYTHONPATH=. python scripts/seed_users.py
```

---

## Testing

```bash
cd backend
pytest -v
```

The test suite covers the full pipeline: submission → background AI processing → retrieval. Completes in ~5 seconds when Hugging Face models are warm.

---

## Project Structure

```
civiclens-dispatch-/
├── backend/
│   ├── .python-version          # Pins Python 3.11.9 for Render
│   ├── app/
│   │   ├── main.py              # FastAPI app, middleware, routers
│   │   ├── auth.py              # JWT creation and verification
│   │   ├── config.py            # Settings from environment variables
│   │   ├── middleware.py        # Request logging middleware
│   │   ├── db/
│   │   │   ├── database.py      # Async database + sync engine
│   │   │   └── models.py        # SQLAlchemy table definitions
│   │   ├── routes/
│   │   │   ├── incidents.py     # CRUD + file upload endpoints
│   │   │   ├── auth_routes.py   # Login, register, /me
│   │   │   ├── analytics.py     # Aggregate statistics
│   │   │   ├── ai_status.py     # AI model health check
│   │   │   └── ws_routes.py     # WebSocket endpoint
│   │   └── services/
│   │       ├── incident_processor.py  # AI pipeline orchestrator
│   │       ├── asr.py                 # Whisper speech-to-text
│   │       ├── classification.py      # BART-MNLI incident classification
│   │       ├── risk_scorer.py         # Risk score calculation
│   │       ├── summarization.py       # BART-CNN summarization
│   │       └── image_analyzer.py      # DETR object detection
│   ├── scripts/
│   │   └── seed_users.py        # Create admin + dispatcher accounts
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── api/client.js        # Central API client (all fetch calls)
│   │   ├── context/
│   │   │   └── AuthContext.jsx  # JWT storage, login/logout state
│   │   ├── components/
│   │   │   ├── dashboard/       # StatsBar, IncidentTable, IncidentDetail
│   │   │   ├── analytics/       # AnalyticsView with Recharts
│   │   │   ├── forms/           # SubmitIncidentForm
│   │   │   └── shared/          # LoadingSpinner, Toast, IncidentCard
│   │   └── pages/
│   │       └── LoginPage.jsx
│   ├── .env.production          # VITE_API_URL for Vercel
│   └── vite.config.js
├── docs/                        # Architecture, API, and learning docs
└── README.md
```

---

## AI Models

| Model | Task | Latency |
|-------|------|---------|
| `openai/whisper-large-v3` | Audio transcription (ASR) | ~10s |
| `facebook/bart-large-mnli` | Incident type + severity classification | ~5s |
| `facebook/bart-large-cnn` | One-sentence summary generation | ~5s |
| `facebook/detr-resnet-50` | Image object detection | ~5s |

All four models run in parallel via `asyncio.gather`. Total pipeline time: ~20–45 seconds depending on HuggingFace load.

---

## Deployment

| Service | Platform | Config |
|---------|----------|--------|
| Frontend | Vercel | Auto-deploy from `main`, `VITE_API_URL` env var |
| Backend | Render (free tier) | `render.yaml` in repo root, Python 3.11.9 |
| Database | Supabase | PostgreSQL, session pooler on port 5432 |
| Monitoring | UptimeRobot | Pings `/` every 5 minutes to prevent Render sleep |

---

## Roadmap

- [x] Days 1–7 — Python, FastAPI basics, Git
- [x] Days 8–14 — Database design, SQLAlchemy, CRUD
- [x] Days 15–21 — Async processing, file uploads, testing
- [x] Days 22–30 — React frontend, dashboard UI
- [x] Days 31–40 — Audio pipeline (Whisper ASR)
- [x] Days 41–50 — Vision models, text classification, parallel pipeline
- [x] Days 51–60 — Frontend polish, analytics, full test suite
- [x] Days 61–70 — Analytics dashboard, WebSockets, real-time feed
- [x] Days 71–74 — JWT auth, role-based access, production deployment
- [x] Day 75 — End-to-end verification, monitoring, v1.0.0 released

---

## Author

**Suhas Bharthepude**
- GitHub: [@Suhas-Bharthepude](https://github.com/Suhas-Bharthepude)
- Email: bharthepude.s@northeastern.edu

*Built in 75 days as a structured full-stack + AI learning project.*
