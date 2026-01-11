Below is a 75‑day roadmap (about 2.5 months). You can stretch or compress weeks if needed, but keep the order. Each day lists: what to learn, why, how it applies, and exactly what to do.

Days 1–7: Project vision, Git, and Python setup
Day 1 – Clarify scope and install tools

What to learn: Project goals and basic tooling (Python, VS Code setup, GitHub account).

Why: Clear goals keep you focused; GitHub is where recruiters will see your work.

How it applies: You’ll treat CivicLens Dispatch like a real product from day one.

Do today:

Write a one‑page spec (Markdown): problem, users, features (citizen form, dispatcher dashboard, AI pipeline, logs).

Install latest Python, VS Code, and Git.

Create a GitHub repo civiclens-dispatch and clone it.

Day 2 – Git basics

What to learn: git add, commit, push, branching.

Why: Version control is essential for any software engineer.

How it applies: You’ll commit daily and show a clean history to employers.

Do today:

Initialize repo, create .gitignore (for Python, venv).

Practice: make a notes/ folder, add a file, commit, push.

Create a roadmap.md and paste this plan, committing it.

Day 3 – Python environments and project skeleton

What to learn: Virtual environments and basic project layout.

Why: Keeps dependencies isolated and reproducible.

How it applies: Your backend and ML code will run reliably on any machine.

Do today:

In VS Code terminal: create venv (python -m venv .venv), select it as interpreter.

Create folders: backend/, frontend/, infra/, docs/.

Inside backend/, add app/ with empty __init__.py and main.py.

Day 4 – Python HTTP basics (requests, JSON)

What to learn: Using HTTP from Python and handling JSON.

Why: Your app will call external APIs (maps, possibly hosted models).

How it applies: Incident geocoding and any external AI endpoints.

Do today:

Write a small script in backend/playground/http_playground.py that calls a public JSON API (e.g., a simple “hello world” public endpoint) and prints results.

Parse JSON into Python dicts and access fields.

Day 5 – Intro to web APIs and REST

What to learn: REST concepts: routes, methods (GET/POST), status codes.

Why: Your backend will expose REST endpoints to the frontend.

How it applies: /incidents, /submit, /health etc.

Do today:

In docs/concepts.md, summarize: what is an endpoint, route, method, status code, JSON body.

Sketch which endpoints CivicLens needs (list them with path + method).

Day 6 – FastAPI basics (hello world)

What to learn: FastAPI app, simple route.

Why: FastAPI is your backend framework.

How it applies: All backend logic will live in FastAPI endpoints.

Do today:

Install FastAPI and an ASGI server (uvicorn).

In backend/app/main.py, create a basic app with a /health GET endpoint returning {"status": "ok"}.

Run with uvicorn app.main:app --reload and hit it in browser.

Day 7 – FastAPI path & query parameters

What to learn: Handling parameters in routes.

Why: You’ll receive incident IDs, filters, pagination parameters.

How it applies: /incidents/{id}, /incidents?severity=high.

Do today:

Add a route /echo/{name} returning {"hello": name}.

Add a route /incidents_dummy that returns mock list filtered by query param severity.

Days 8–14: Data modeling and PostgreSQL basics
Day 8 – Pydantic models

What to learn: Pydantic (FastAPI’s data models).

Why: You need consistent schema for incidents, users, and AI outputs.

How it applies: Request and response types like IncidentCreate, IncidentRead.

Do today:

Create backend/app/schemas/incident.py with simple Pydantic models: IncidentCreate, IncidentBase, IncidentRead.

Use them in your dummy endpoints’ responses.

Day 9 – Intro to relational databases and PostgreSQL

What to learn: Tables, rows, primary keys, foreign keys; what PostgreSQL is.

Why: You’ll persist incidents, users, and logs.

How it applies: A real dispatcher needs historical data.

Do today:

Install PostgreSQL locally (or use a cloud dev instance).

Create a database civiclens.

Write notes in docs/database.md explaining: table, schema, primary key, foreign key.

Day 10 – SQL basics

What to learn: CREATE TABLE, INSERT, SELECT, UPDATE, DELETE.

Why: Understanding raw SQL helps debug and design schemas.

How it applies: Incident table definitions and debugging queries.

Do today:

Use psql or GUI to create a simple incidents table with a few columns.

Insert a few rows and query them. Save example SQL in backend/sql/experiments.sql.

Day 11 – SQLAlchemy intro

What to learn: SQLAlchemy ORM basics.

Why: Lets you manipulate DB via Python classes.

How it applies: Clean Python code for incident CRUD.

Do today:

Install SQLAlchemy and a Postgres driver.

Create backend/app/db/database.py with engine and session setup.

Define Incident ORM model in backend/app/db/models.py.

Day 12 – Integrate FastAPI + SQLAlchemy

What to learn: Dependency injection for DB sessions in FastAPI.

Why: Each request needs a DB connection.

How it applies: All endpoints reading/writing incidents.

Do today:

Create backend/app/dependencies.py with get_db function.

Add POST /incidents route that writes a row to DB using ORM, returning the stored incident.

Day 13 – GET endpoints and pagination basics

What to learn: Reading from DB with filters.

Why: Dispatcher dashboard needs list & detail views.

How it applies: /incidents, /incidents/{id}.

Do today:

Implement GET /incidents with limit/offset query parameters.

Implement GET /incidents/{id}; return 404 if not found.

Day 14 – Refactor into modules & write seed script

What to learn: Organizing code by feature.

Why: Keeps project manageable as it grows.

How it applies: Separate routers, schemas, services.

Do today:

Create backend/app/routers/incidents.py and move incident endpoints there.

In main.py, include_router.

Write a small backend/scripts/seed_incidents.py that inserts fake incidents.

Days 15–21: Async processing and basic AI placeholders
Day 15 – Background tasks / queues conceptually

What to learn: Why background jobs, basics of queues (e.g., Redis + worker).

Why: Audio/image processing can be slow; don’t block requests.

How it applies: Submitting incidents quickly, processing AI in the background.

Do today:

Read about background tasks and job queues.

Document in docs/architecture.md how an incident moves through your system.

Day 16 – Simple FastAPI BackgroundTasks

What to learn: FastAPI’s built‑in BackgroundTasks.

Why: Easy way to start async processing before full queue.

How it applies: Kick off AI processing after insert.

Do today:

Modify POST /incidents to schedule a background function that currently just logs “process incident X”.

Day 17 – File uploads in FastAPI (images, audio)

What to learn: Handling multipart uploads.

Why: Citizens will upload audio and photos.

How it applies: /upload endpoint or extended /incidents endpoint.

Do today:

Add endpoints accepting UploadFile for image and audio.

Store files temporarily in backend/media/tmp/.

Day 18 – S3‑style storage conceptually

What to learn: Object storage vs local disk.

Why: Scalable media storage is important for real apps.

How it applies: Where you keep audio and images.

Do today:

Read about S3 buckets and how to access them from Python.

Decide: start local (disk) now, plan S3 later; note this in docs/architecture.md.

Day 19 – Introduce basic config & env variables

What to learn: Using environment variables for secrets and config.

Why: DB URIs, API keys, etc. must not be hardcoded.

How it applies: Postgres URL, S3 keys, map API key.

Do today:

Create .env (don’t commit it) and load with a config module.

Store DB URL and debug flag there.

Day 20 – Testing basics with pytest

What to learn: Unit tests & simple API tests.

Why: Tests show professionalism and help refactor safely.

How it applies: Testing incident creation & listing.

Do today:

Install pytest, create backend/tests/test_incidents.py.

Write one test that hits /health and one that tests POST /incidents with test DB.

Day 21 – Buffer/cleanup & mini review

What to learn: Review concepts so far.

Why: Consolidation prevents gaps later.

How it applies: You’ll be ready to add ML.

Do today:

Clean up folder names, comments.

Update docs/architecture.md with your actual endpoints and data flow.

Days 22–30: Frontend fundamentals (React)
Day 22 – Web basics: HTML/CSS/JS

What to learn: Structure of web pages, styling, scripts.

Why: React builds on these.

How it applies: Dispatcher dashboard and citizen form.

Do today:

Read intro tutorials on HTML, CSS, and JavaScript.

Create frontend/vanilla-prototype.html that contains a simple form and an empty table.

Day 23 – React concepts

What to learn: Components, props, state.

Why: React will power your UI.

How it applies: Incident list, incident detail panel.

Do today:

Use a React starter (e.g., Vite or similar).

Create frontend/ app with a root App component displaying “CivicLens”.

Day 24 – Fetching from backend in React

What to learn: fetch/axios, useEffect, promises.

Why: The frontend must talk to your FastAPI.

How it applies: Query /incidents and display results.

Do today:

Implement a call to /health and show API status on the page.

Day 25 – Incident list UI

What to learn: Rendering lists, tables, and loading/error states.

Why: Dispatcher needs to see many incidents at once.

How it applies: Main dashboard view.

Do today:

Implement IncidentList component that fetches /incidents and displays key columns in a table.

Day 26 – Incident detail panel

What to learn: React routing or conditional rendering.

Why: Need detail view on click.

How it applies: Show full description, severity, media links.

Do today:

When user clicks a row, show detail panel using /incidents/{id}.

Day 27 – Citizen submission form UI

What to learn: Controlled forms, file inputs.

Why: Users need a way to submit incidents.

How it applies: Text, location, optional audio/image.

Do today:

Add a SubmitIncident page with fields: text description, optional severity, file inputs.

Wire it to POST /incidents (for now ignore files or send separately).

Day 28 – Basic styling and layout

What to learn: Layout components (flexbox), a UI library (e.g., MUI/Chakra).

Why: Visual polish matters in a portfolio.

How it applies: Clean dispatcher dashboard, clear hierarchy.

Do today:

Add a UI library and create a simple two‑column layout (list on left, detail on right).

Day 29 – Error handling and loading states

What to learn: Handling failed requests gracefully.

Why: Real apps fail; UX should explain why.

How it applies: Show errors if backend is down.

Do today:

Add loading spinners and error messages for main views.

Day 30 – Frontend cleanup and docs

What to learn: Organizing frontend file structure.

Why: Keeps code readable for reviewers.

How it applies: Better impression on GitHub.

Do today:

Create frontend/src/components, pages, api folders.

Move components into logical places, update imports.

Days 31–40: Audio pipeline (ASR) and incident enrichment
Day 31 – Audio basics and recording/upload UX

What to learn: Audio formats (WAV, MP3), browser file inputs.

Why: Users will upload voice notes.

How it applies: Input to ASR model.

Do today:

Ensure your form can upload an audio file.

Store temporarily on backend and save path in DB.

Day 32 – Intro to speech recognition models

What to learn: How modern ASR works conceptually.

Why: You will treat your ASR model as a black box but should understand its role.

How it applies: Turning caller speech into text for classification.

Do today:

Read an overview of open ASR models (e.g., Whisper‑style) and how to call them from Python.

Day 33 – Build ASR service function

What to learn: Calling an ASR model or API from Python.

Why: Core to converting audio to incident text.

How it applies: You’ll call this in the background job.

Do today:

Create backend/app/services/asr.py with a transcribe_audio(path) function that returns mock text first, then wire in a real model/API later.

Day 34 – Connect ASR to incident creation

What to learn: Chaining background tasks.

Why: When new incident with audio is created, transcribe automatically.

How it applies: Auto‑fills description for dispatcher.

Do today:

Modify background job to call transcribe_audio if audio is present and store transcript in DB.

Day 35 – Display transcript in UI

What to learn: Updating API responses and frontend models.

Why: Dispatcher should see transcript next to incident.

How it applies: Better triage.

Do today:

Add transcript field to incident schema and DB.

Show transcript in incident detail panel.

Day 36 – Map/geocoding integration

What to learn: Using a maps/geocoding API.

Why: Incidents need locations on a map.

How it applies: Reverse geocode coordinates and show in frontend map.

Do today:

Register for a map API; store key in .env.

Write backend/app/services/geocode.py to convert lat/lon to address.

Day 37 – Location UI

What to learn: Map display in React (e.g., a simple embed or JS SDK).

Why: Dispatchers benefit from spatial context.

How it applies: Show incident pin on map.

Do today:

Add a small map component and place a marker for selected incident.

Day 38 – Summarization concept and dummy function

What to learn: What text summarization is and when to use it.

Why: You’ll summarize multi‑modal info for dispatchers.

How it applies: Concise “AI summary” field.

Do today:

Create backend/app/services/summarization.py with function summarize_incident(text_fields) returning a short bullet string (hard‑coded or simple heuristics for now).

Day 39 – Wire summarization into pipeline

What to learn: Combining text fields for summarization.

Why: Provide quick overview for each incident.

How it applies: Show “AI summary” column in list.

Do today:

After ASR, call summarization service and store result in summary column.

Expose summary in APIs and display in the list view.

Day 40 – Buffer / integration testing

What to learn: End‑to‑end validation.

Why: Ensure audio → transcript → summary works.

How it applies: Confidence building and debugging early.

Do today:

Manually test: submit incident with audio; confirm DB row and UI updates.

Fix any bugs and document flow in docs/pipeline.md.

Days 41–50: Vision + classification + scoring
Day 41 – Image classification and object detection concepts

What to learn: Basics of image classification vs detection.

Why: Need to understand what your model outputs.

How it applies: Detect vehicles, fire, etc. from incident images.

Do today:

Write short notes on how classification vs detection differ and what outputs to expect.

Day 42 – Vision service stub

What to learn: Designing service interfaces.

Why: Keeps model integration clean.

How it applies: analyze_image(path) returning a simple dict.

Do today:

Create backend/app/services/vision.py with stub that returns fake labels and counts.

Day 43 – Integrate image pipeline

What to learn: Extending your background worker.

Why: Process images when present.

How it applies: Enrich incident row with labels and risk flags.

Do today:

In background job, call analyze_image if image is present and store labels in DB as JSON.

Day 44 – Text classification (incident type, severity)

What to learn: Text classification basics.

Why: Auto‑tag incident type and severity.

How it applies: Filter and rank incident list.

Do today:

Create backend/app/services/text_classification.py with classify_incident(text) returning type and severity.

Day 45 – Scoring logic and fusion

What to learn: Combining signals into a risk score.

Why: Dispatcher needs a single sortable metric.

How it applies: Score based on text severity + vision labels.

Do today:

Create backend/app/services/scoring.py that accepts transcript, image labels, etc., and computes a numeric risk_score.

Add risk_score column to DB.

Day 46 – List sorting and filtering in UI

What to learn: Sorting/filtering in React tables.

Why: Helps triage high‑risk incidents first.

How it applies: Sort by risk_score, filter by severity/type.

Do today:

Add UI controls and implement client‑side sorting; optionally add backend query parameters for server‑side filtering.

Day 47 – Confidence and explanation display

What to learn: Communicating AI decisions.

Why: Recruiters look for responsible AI thinking.

How it applies: Show “why” behind scores.

Do today:

Add explanation fields to scoring output (e.g., rules triggered) and display them in incident detail.

Day 48 – Redaction feature (privacy)

What to learn: Simple image manipulation.

Why: Demonstrates ethical considerations (blur faces/plates).

How it applies: Optional toggle to redact stored images.

Do today:

Use a simple method (e.g., blur entire image or defined bounding boxes from vision pipeline) and save a redacted copy.

Day 49 – End-to-end AI dry run

What to learn: Full flow with your stubs or partial models.

Why: Ensure architecture is sound before real models.

How it applies: You’ll only swap in real models later.

Do today:

Submit incidents with text, audio, and image; track each step and confirm all fields are filled.

Day 50 – Documentation sprint

What to learn: Writing technical docs.

Why: Docs make your project stand out.

How it applies: Recruiters can understand your design quickly.

Do today:

Update docs/architecture.md with diagrams (text‑based now; later you can add real diagrams) describing each service and data flow.

Days 51–60: Real model integrations, monitoring, and polish
Day 51 – Real ASR integration

What to learn: Replacing stubs with actual model/service calls.

Why: Makes your pipeline truly AI‑powered.

How it applies: Production‑style transcription.

Do today:

Update transcribe_audio to call a real ASR model/API, handle errors, and log latency; keep tests passing.

Day 52 – Real text classifier

What to learn: Using a real classification model.

Why: Improve accuracy of type/severity tags.

How it applies: Better incident triage.

Do today:

Replace classify_incident stub with real model/API calls and adjust scoring logic if needed.

Day 53 – Real summarization model

What to learn: Calling summarization models and prompt design (if needed).

Why: Good summaries are recruiter‑visible.

How it applies: Crisp, human‑readable summary field.

Do today:

Update summarize_incident to use a real summarization model; test on a few example incidents.

Day 54 – Real vision model

What to learn: Handling vision model inputs/outputs.

Why: Image understanding is a key differentiator.

How it applies: Correctly detect scene features.

Do today:

Replace analyze_image stub with a real image classifier/detector; map labels to your risk logic.

Day 55 – Metrics and logging

What to learn: Basic metrics (latency, error counts) and structured logging.

Why: Shows scalability and production mindset.

How it applies: You can talk about performance trade‑offs in interviews.

Do today:

Introduce timing decorators or middleware to log request durations and store them in a simple table or log file.

Day 56 – Basic authentication (optional but valuable)

What to learn: Simple login with hashed passwords or token-based auth.

Why: Real dashboards are not public.

How it applies: Restrict dispatcher dashboard.

Do today:

Add a simple users table and login endpoint, and protect dispatcher routes with a basic token scheme.

Day 57 – UI polish and usability

What to learn: UX improvements, layout tweaks.

Why: Good UX is memorable in demos.

How it applies: Clean, professional look.

Do today:

Improve typography, spacing, and color palette; add tooltips for AI explanation fields.

Day 58 – Load testing basics

What to learn: Simple performance tests (many incident submissions).

Why: Lets you mention performance numbers on resume.

How it applies: Simulate busy periods (many citizen reports).

Do today:

Write a small Python script that posts many fake incidents and measure average response time; record results in docs/performance.md.

Day 59 – Write unit and integration tests for AI services

What to learn: Testing AI‑calling functions.

Why: Ensures pipeline doesn’t break when changing models.

How it applies: Validate expected keys and shapes.

Do today:

Add tests for ASR, classification, vision services using mocked or fixed responses.

Day 60 – Mid‑project cleanup and freeze

What to learn: Code review and refactoring.

Why: Prepares you for the “portfolio ready” phase.

How it applies: Cleaner code and fewer regrets later.

Do today:

Remove dead code and commented blocks, ensure linting, and update any outdated docs.

Days 61–75: Storytelling, demos, and resume integration
Day 61 – Demo script and sample data

What to learn: How to tell a story during a demo.

Why: Recruiters remember narratives, not just APIs.

How it applies: You’ll show “before/after” for dispatchers.

Do today:

Create a scripted series of sample incidents (text/audio/image) and a written demo script in docs/demo_script.md.

Day 62 – README and screenshots

What to learn: Writing a great README.

Why: It’s the first thing visitors see on GitHub.

How it applies: Explains value, architecture, and how to run the app.

Do today:

Update README.md with: problem, solution, tech stack, features, architecture diagram (even ASCII), and setup steps; add screenshots of dashboard and incident flow.

Day 63 – Short architecture overview slide deck

What to learn: Communicating architecture visually.

Why: Useful in interviews and portfolio sites.

How it applies: Summarizes your design quickly.

Do today:

Create a simple slide deck (3–5 slides) describing system components and main pipeline; save in docs/slides/.

Day 64 – Resume bullet drafting

What to learn: Translating project into resume language.

Why: Many students fail to sell their projects well.

How it applies: You’ll highlight AI, backend, and UX depth.

Do today:

Draft 3–5 resume bullets (as discussed earlier) and store them in docs/resume_bullets.md.

Day 65 – Portfolio website (optional but strong)

What to learn: Simple personal site or GitHub Pages.

Why: Central place to showcase projects.

How it applies: Link to CivicLens with screenshots and explanation.

Do today:

Create a single‑page site describing the project and embed screenshots or a short GIF/video of the app.

Day 66 – Record video walkthrough

What to learn: Screen recording and narration.

Why: Recruiters may watch a 2–3 minute demo.

How it applies: You can link the video directly on your resume or portfolio.

Do today:

Record a short video showing submission of an incident and dispatcher triage, explaining each AI step.

Day 67 – Add configuration for prod vs dev

What to learn: Environment separation.

Why: Professional apps have different configs for dev/prod.

How it applies: Different DB URLs, debug mode, etc.

Do today:

Add config class that reads environment (DEV/PROD) and adjusts log level, DB URL, and any external endpoints.

Day 68 – Containerization (Docker)

What to learn: Dockers basics (Dockerfile, docker-compose).

Why: Makes your project easy to run anywhere.

How it applies: You can mention containerization and simple orchestration.

Do today:

Create Dockerfile for backend and docker-compose.yml for backend + database; ensure docker compose up runs your stack.

Day 69 – Final end‑to‑end QA

What to learn: Testing like a user.

Why: You want a stable public demo.

How it applies: Catch edge cases and UX issues.

Do today:

Go through the whole app as both citizen and dispatcher; note and fix critical bugs only.

Day 70–75 – Buffer, refinement, and stretch goals

What to learn: Iteration and polish.

Why: Adds “extras” that make you stand out.

How it applies: Possible stretch tasks:

Add WebSockets for live updates.

Add analytics page (incident volume over time).

Improve auth (roles: admin vs dispatcher).

Do each day:

Choose one extra feature per day to implement and test.

How your VS Code project should look
By the end, your VS Code workspace (opened at the repo root) should look roughly like this:

text
civiclens-dispatch/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── dependencies.py
│   │   ├── config.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   └── incidents.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── incident.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── models.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── asr.py
│   │   │   ├── text_classification.py
│   │   │   ├── summarization.py
│   │   │   ├── vision.py
│   │   │   └── scoring.py
│   │   └── media/
│   │       └── tmp/
│   ├── scripts/
│   │   └── seed_incidents.py
│   ├── tests/
│   │   └── test_incidents.py
│   ├── sql/
│   │   └── experiments.sql
│   ├── requirements.txt
│   └── .env        # not committed
├── frontend/
│   ├── package.json
│   ├── vite.config.*  # or similar
│   └── src/
│       ├── main.tsx / main.jsx
│       ├── App.tsx / App.jsx
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   ├── IncidentList.tsx
│       │   ├── IncidentDetail.tsx
│       │   └── MapView.tsx
│       └── pages/
│           ├── DashboardPage.tsx
│           └── SubmitIncidentPage.tsx
├── infra/
│   ├── docker-compose.yml
│   └── Dockerfile
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── pipeline.md
│   ├── performance.md
│   ├── demo_script.md
│   ├── resume_bullets.md
│   └── slides/
├── notes/
│   └── learning-notes.md
├── README.md
├── .gitignore
└── .venv/   # local virtual environment