# CivicLens Dispatch — Live Demo Script

> **Total time:** ~4–5 minutes  
> **Audience:** Technical recruiters, hiring managers, engineers  
> **Format:** Use for live interviews, recorded video, or portfolio presentations  
>
> Practice this until you can do it without reading it.
> The goal is to sound natural, not scripted.

---

## Before You Start (Setup Checklist)

Run these before the demo — don't do setup live, it kills momentum.

```bash
# Terminal 1 — Backend
cd backend && uvicorn app.main:app --reload

# Terminal 2 — Frontend
cd frontend && npm run dev
```

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:5173
- [ ] At least 8–10 seeded incidents visible in the dashboard
- [ ] Browser tab open to the dashboard (not the terminal)
- [ ] Browser tab open to http://localhost:8000/docs (API docs)
- [ ] Text editor open with a sample incident description ready to paste

**Sample incident text (copy this before the demo):**
```
Major fire at the warehouse on Industrial Boulevard. Thick black smoke 
visible from miles away. Multiple fire trucks responding. At least two 
workers reported trapped on the second floor. Explosions heard from inside.
```

---

## The Demo (Word for Word)

### Opening — The Problem (30 seconds)

> "Emergency dispatch centers deal with a flood of unstructured reports — 
> text messages, voice recordings, photos — from citizens, sensors, and 
> field units. Every one of those reports needs to be read, classified 
> by incident type, scored for urgency, and summarized before a dispatcher 
> can act on it. That process is manual, slow, and error-prone under pressure.
>
> I built CivicLens Dispatch to automate that triage pipeline using 
> multimodal AI. Let me show you how it works."

*[Open the dashboard]*

---

### Part 1 — Show the Dashboard (45 seconds)

> "This is the dispatcher's view. Every incident in the system is listed here, 
> pre-sorted by risk score — highest urgency at the top."

*[Point to the risk score column]*

> "Each row already has the AI-generated fields: incident type, severity 
> classification, and a risk score between 0 and 1. The dispatcher didn't 
> have to assign any of these — the AI pipeline did it automatically."

*[Click a high-severity incident to open the detail panel]*

> "In the detail panel, you can see everything the pipeline produced: 
> the incident type, severity, risk score, a one-sentence summary, and 
> if there was audio or an image attached, the transcript and image 
> description appear here too."

*[Close the panel]*

---

### Part 2 — Submit a New Incident Live (90 seconds)

> "Now let me show you the pipeline working in real time."

*[Open the submit form]*

> "I'll submit a new incident — just text, no audio or image — and 
> watch what the AI produces."

*[Paste the sample fire incident text, fill in location as "500 Industrial Blvd", source as "citizen", submit]*

> "The API returned immediately — 201 Created. The incident is now in 
> the database with no AI fields yet."

*[Point to the new incident at the bottom of the list — no type/severity/risk yet]*

> "The AI pipeline is running in the background. This is important — 
> the API doesn't block waiting for AI inference. It responds instantly 
> and processes asynchronously."

*[Wait 5–10 seconds, then refresh or watch the row update]*

> "And there it is. The pipeline classified this as 'fire', severity 
> 'high', risk score around 75%. It generated a summary. All of that 
> happened in about 5 seconds — automatically, in the background."

---

### Part 3 — Show the Architecture (60 seconds)

> "Let me explain what just happened under the hood."

*[Pull up a simple diagram or describe verbally — optionally switch to a whiteboard or slide]*

> "The pipeline runs in two parallel phases using asyncio.gather().
>
> Phase 1: If there's audio, Whisper transcribes it. If there's an 
> image, DETR analyzes it. Both run simultaneously.
>
> Phase 2: Once we have all the text — description plus any transcript 
> or image caption — three more tasks run in parallel: BART-MNLI 
> classifies the incident type and severity, BART-CNN generates a 
> summary, and another BART-MNLI call scores urgency from 0 to 1.
>
> The reason for two phases is that Phase 2 needs the transcript from 
> Phase 1. Within each phase, tasks are independent, so they run 
> simultaneously."

*[Optional: switch to the API docs tab]*

> "The backend is a FastAPI app with full async support. I can show 
> you the Swagger docs — every endpoint is documented, typed, and 
> tested."

---

### Part 4 — Show the Tests (30 seconds)

> "The system has three test suites."

*[Optionally flip to terminal and run one]*

```bash
PYTHONPATH=. python scripts/test_e2e.py
```

> "Six end-to-end tests covering the full request lifecycle — health, 
> AI status, create, pipeline completion, reprocess, and search. All 
> passing. There are also 14 error handling tests validating every 
> invalid input scenario, and a performance test suite that benchmarks 
> query times."

---

### Closing — What I'd Build Next (30 seconds)

> "If I were to take this further, the next steps would be deploying 
> to a cloud provider — the backend is straightforward to containerize, 
> and I'd swap SQLite for PostgreSQL. I'd also add real-time updates 
> via WebSockets so the dashboard updates live without a refresh.
>
> The thing I'm most proud of technically is the parallel async pipeline. 
> Getting asyncio.gather() right across multiple Hugging Face API calls, 
> with proper error isolation so one failing model doesn't kill the 
> others — that took real debugging and taught me a lot about async 
> Python."

---

## Anticipated Questions + Answers

**"Why FastAPI over Flask or Django?"**
> FastAPI is async-native — I needed that for the background AI processing. Flask is sync by default and Django is overkill for an API-only backend. FastAPI also has automatic Swagger docs and Pydantic validation built in, which saved a lot of boilerplate.

**"Why SQLite? Isn't that just for toys?"**
> For development and a portfolio project at this scale, SQLite is completely appropriate — it's fast, zero-config, and file-based. The database layer is abstracted through SQLAlchemy, so swapping to PostgreSQL for production is a config change, not a rewrite. I set it up this way intentionally.

**"How accurate is the AI classification?"**
> For clear incidents — fires, medical emergencies, traffic accidents — accuracy is high. The zero-shot models perform well on unambiguous language. Ambiguous reports ("something weird happening on Main St") are harder and the model defaults to lower confidence scores, which is appropriate — a dispatcher should review low-confidence results.

**"What would you do differently?"**
> I'd add Celery + Redis for the background task queue instead of FastAPI's built-in BackgroundTasks. The built-in approach works, but it doesn't survive server restarts — if the server crashes mid-pipeline, the job is lost. A proper task queue gives you persistence and retry logic.

**"How long did this take?"**
> 61 days of daily work, structured as a learning roadmap. Each day I built one feature or concept, committed it, and documented what I learned. The commit history on GitHub shows the progression.

---

## Recovery Lines (If Things Break)

**If the backend is down:**
> "Let me restart it — this happens with the Hugging Face free tier occasionally going cold." *(restart, continue)*

**If the AI pipeline is slow:**
> "The Hugging Face free tier has cold start latency — models spin down when idle. In a production setup you'd run models locally or use a paid API with always-on instances. Let me show you a pre-processed incident while it loads."

**If the frontend isn't loading:**
> "Let me use the API docs directly — that's actually a cleaner way to show the endpoints anyway." *(switch to localhost:8000/docs)*

---

## Video Recording Notes

When recording a demo video (Day 62–63), use this structure:

| Segment | Time | What to Show |
|---|---|---|
| Problem statement | 0:00–0:30 | Just your voice, no screen |
| Dashboard overview | 0:30–1:15 | Screen: dashboard with existing incidents |
| Live pipeline demo | 1:15–2:45 | Screen: submit form → watch AI populate |
| Architecture explanation | 2:45–3:30 | Diagram or whiteboard |
| Tests + closing | 3:30–4:00 | Terminal or just voice |

**Recording tips:**
- Use QuickTime (Mac) or OBS to record
- Record at 1080p, crop to just the browser window
- Speak slower than you think you need to
- Do 2–3 takes, use the best one
- Keep it under 5 minutes — recruiters won't watch longer