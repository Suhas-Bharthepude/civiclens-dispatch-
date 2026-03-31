# backend/app/services/incident_processor.py
#
# Incident Processing Pipeline — orchestrates all AI services.
# Runs in the background after an incident is created or audio is uploaded.
#
# This file is the "conductor" — it calls each AI service in order
# and saves all the results back to the database.
#
# Current AI pipeline status:
#   ✅ Step 1: Fetch incident from database
#   ✅ Step 2: Transcribe audio (real ASR via Hugging Face Whisper)
#   ✅ Step 3: Classify incident type and severity (keyword-based stub)
#   ✅ Step 4: Summarize incident (real NLP via Hugging Face BART) ← NEW Day 39
#   ✅ Step 5: Calculate risk score (rule-based stub)
#   ✅ Step 6: Save all AI results to database
#
# Future days will replace stubs 3 and 5 with real models.

# asyncio for async/await support and sleep delays
import asyncio

# datetime for generating readable log timestamps
from datetime import datetime

# database is the async connection to SQLite (or PostgreSQL in production)
from app.db.database import database

# incidents is the SQLAlchemy table object — used to build SQL queries
from app.db.models import incidents

# transcribe_audio converts uploaded audio files to text using Whisper
# This was built in Day 33 and integrated in Day 34
from app.services.asr import transcribe_audio

# summarize_incident generates a clean summary paragraph using BART
# This is the new Day 39 addition — replaces the string-formatting stub
from app.services.summarization import summarize_incident


# ============================================================
# MAIN PIPELINE FUNCTION
# ============================================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    Run the full AI processing pipeline for one incident.

    Called automatically in the background by incidents.py
    (the FastAPI route) after:
      - A new incident is created (POST /incidents)
      - Audio is uploaded to an incident (POST /incidents/{id}/audio)

    The function fetches the incident, runs all AI services on it,
    and updates the database with the results.

    Args:
        incident_id:  The database ID of the incident to process
        log_message:  Optional string for extra context in logs
    """

    # Generate a timestamp string for all log lines in this pipeline run
    # Format: "14:22:05" — makes logs easy to read in the terminal
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Print a clear separator in the logs so each pipeline run is easy to find
    print(f"[{timestamp}] {'='*60}")
    print(f"[{timestamp}] 🤖 PROCESSING INCIDENT #{incident_id}")
    if log_message:
        # Print any extra context provided by the caller
        print(f"[{timestamp}] Context: {log_message}")
    print(f"[{timestamp}] {'='*60}")


    # ── STEP 1: FETCH INCIDENT FROM DATABASE ─────────────
    print(f"[{timestamp}] 📋 Fetching incident from database...")

    # Build a SELECT query: SELECT * FROM incidents WHERE id = incident_id
    select_query = incidents.select().where(incidents.c.id == incident_id)

    # Execute the query asynchronously and get the first (only) matching row
    incident = await database.fetch_one(select_query)

    # If no incident was found with this ID, something went wrong
    # Log the error and stop processing — can't proceed without data
    if not incident:
        print(f"[{timestamp}] ❌ Incident #{incident_id} not found in database!")
        return

    # Convert the database row to a regular Python dictionary
    # This makes it easier to access fields by name: incident["description"]
    incident = dict(incident)

    print(f"[{timestamp}] ✅ Found incident: '{incident['description'][:50]}...'")


    # ── STEP 2: TRANSCRIBE AUDIO (REAL) ──────────────────
    # If the incident has an audio file attached, transcribe it to text.
    # The transcript is used by both summarization (Step 4) and classification (Step 3).

    # transcript starts as None — stays None if no audio was uploaded
    transcript = None

    if incident.get("audio_path"):
        # An audio file exists for this incident
        print(f"[{timestamp}] 🎤 Audio file found: {incident['audio_path']}")
        print(f"[{timestamp}] 🎤 Starting transcription...")

        try:
            # Call the ASR service — returns the transcript as a string
            # This may take 5-30 seconds depending on audio length and API load
            transcript = await transcribe_audio(incident["audio_path"])
            print(f"[{timestamp}] ✅ Transcription complete: '{transcript[:60]}...'")

        except Exception as e:
            # Transcription failed — log the error but continue processing
            # The rest of the pipeline can still run without a transcript
            print(f"[{timestamp}] ⚠️  Transcription failed: {e}")
            # Store an error indicator in the transcript field
            transcript = f"[Transcription failed: {str(e)[:100]}]"

    else:
        # No audio file on this incident
        print(f"[{timestamp}] ℹ️  No audio file — skipping transcription")


    # ── STEP 3: CLASSIFY INCIDENT (STUB) ─────────────────
    # Determine the incident type (fire, medical, crime, etc.)
    # and severity (low, medium, high, critical).
    #
    # Currently a keyword-based stub — will be replaced with a real
    # NLP classification model in a future day (Day 44-45).

    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")

    # Build the text we'll classify from
    # Use description + transcript if available for better accuracy
    description_lower = incident["description"].lower()
    text_to_classify = description_lower

    if transcript and not transcript.startswith("["):
        # Transcript looks like real text — add it to classification input
        text_to_classify += " " + transcript.lower()

    # Simple keyword matching (STUB — real model coming in Day 44)
    if any(w in text_to_classify for w in ["fire", "smoke", "flames", "burning", "smoke detector"]):
        incident_type = "fire"
        severity = "high"
    elif any(w in text_to_classify for w in ["medical", "injured", "hurt", "ambulance", "unconscious", "bleeding"]):
        incident_type = "medical"
        severity = "high"
    elif any(w in text_to_classify for w in ["accident", "crash", "collision", "vehicle", "car crash"]):
        incident_type = "traffic"
        severity = "medium"
    elif any(w in text_to_classify for w in ["noise", "complaint", "loud", "disturbance"]):
        incident_type = "noise"
        severity = "low"
    elif any(w in text_to_classify for w in ["break", "robbery", "theft", "stolen", "steal", "intruder", "break-in"]):
        incident_type = "crime"
        severity = "high"
    elif any(w in text_to_classify for w in ["water", "flood", "leak", "pothole", "road", "infrastructure"]):
        incident_type = "infrastructure"
        severity = "medium"
    else:
        incident_type = "other"
        severity = "medium"

    print(f"[{timestamp}] ✅ Classified as: {incident_type} (severity: {severity})")


    # ── STEP 4: SUMMARIZE INCIDENT (REAL) ─────────────────
    # Generate a clear, concise summary paragraph for the dispatcher.
    #
    # Day 39: This is now real AI (facebook/bart-large-cnn via Hugging Face).
    # Previously this was a string-formatting stub.
    #
    # The summarize_incident() function:
    #   - Combines description + transcript
    #   - Checks if text is long enough to summarize
    #   - Calls Hugging Face BART model
    #   - Falls back to mock if API fails

    print(f"[{timestamp}] 📝 Generating AI summary...")

    try:
        # Call the summarization service
        # Pass both the description and transcript (transcript may be None)
        summary = await summarize_incident(
            description=incident["description"],
            transcript=transcript if transcript and not transcript.startswith("[") else None
            # Only pass transcript if it's real text, not an error message
        )
        print(f"[{timestamp}] ✅ Summary generated: '{summary[:80]}...'")

    except Exception as e:
        # summarize_incident() already handles its own errors and fallbacks,
        # so this outer try/except is an extra safety net.
        # If something completely unexpected happens, use a simple fallback.
        print(f"[{timestamp}] ⚠️  Summary generation failed unexpectedly: {e}")
        summary = f"{incident_type.capitalize()} incident reported. Review description for details."


    # ── STEP 5: CALCULATE RISK SCORE (STUB) ───────────────
    # Score from 0.0 to 1.0 representing urgency/danger level.
    # Higher = more urgent, triggers red highlighting in the dashboard.
    #
    # Currently rule-based (STUB) — will be replaced with a real ML model
    # that considers many factors in a future day (Day 45-47).

    print(f"[{timestamp}] ⚠️  Calculating risk score...")

    # Base score from severity classification
    if severity == "high":
        risk_score = 0.85
    elif severity == "critical":
        risk_score = 0.95
    elif severity == "medium":
        risk_score = 0.55
    else:
        # low severity
        risk_score = 0.25

    # Boost score if urgency keywords appear in the text
    urgency_keywords = ["emergency", "urgent", "critical", "help", "danger", "now", "trapped"]
    if any(word in text_to_classify for word in urgency_keywords):
        # Add 0.10 to the score, but don't exceed 1.0
        risk_score = min(1.0, risk_score + 0.10)

    # Boost if transcript mentions distress
    if transcript and "distress" in transcript.lower():
        risk_score = min(1.0, risk_score + 0.05)

    print(f"[{timestamp}] ✅ Risk score: {risk_score:.2f}")


    # ── STEP 6: SAVE ALL RESULTS TO DATABASE ──────────────
    # Build an UPDATE query that saves all AI-generated fields at once.
    # Using one query is more efficient than multiple separate updates.

    print(f"[{timestamp}] 💾 Saving AI results to database...")

    # Build the UPDATE query
    # .update() creates an UPDATE statement
    # .where() filters to only update this specific incident
    # .values() sets the new values for each field
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            # The real transcript from Whisper ASR (or error message)
            transcript=transcript,
            # The real summary from BART (or mock fallback)
            summary=summary,
            # Stub risk score (will be real ML model later)
            risk_score=risk_score,
            # Stub classification (will be real NLP model later)
            incident_type=incident_type,
            # Stub severity (will be real NLP model later)
            severity=severity,
        )
    )

    # Execute the update query against the database
    await database.execute(update_query)

    # Log successful completion with a summary of what was saved
    print(f"[{timestamp}] ✅ Database updated successfully")
    print(f"[{timestamp}] 📊 Results: type={incident_type}, severity={severity}, "
          f"risk={risk_score:.2f}, has_transcript={transcript is not None}, "
          f"summary_length={len(summary)} chars")
    print(f"[{timestamp}] 🎉 Processing complete for incident #{incident_id}")
    print(f"[{timestamp}] {'='*60}")