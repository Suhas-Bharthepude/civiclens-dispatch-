# backend/app/services/incident_processor.py
#
# Incident Processing Pipeline — orchestrates all AI services.
# Runs in the background after an incident is created or audio is uploaded.
#
# This is the "conductor" — it calls each AI service in order
# and saves all results to the database.
#
# AI pipeline status as of Day 40:
#   ✅ Step 1: Fetch incident from database
#   ✅ Step 2: Transcribe audio  (Whisper via Hugging Face — Day 34)
#   ✅ Step 3: Classify type/severity (BART zero-shot — Day 40) ← NEW TODAY
#   ✅ Step 4: Summarize incident (BART-CNN via Hugging Face — Day 39)
#   🔄 Step 5: Calculate risk score (rule-based stub — Day 45+)
#   ✅ Step 6: Save all AI results to database

# asyncio for async/await and sleep
import asyncio

# datetime for readable log timestamps
from datetime import datetime

# database is the async SQLite/PostgreSQL connection
from app.db.database import database

# incidents is the SQLAlchemy table definition used to build SQL queries
from app.db.models import incidents

# transcribe_audio: converts audio file → text using Whisper (Day 33-34)
from app.services.asr import transcribe_audio

# classify_incident: classifies text → incident type + severity (Day 40 — NEW)
from app.services.classification import classify_incident

# summarize_incident: generates a summary paragraph using BART (Day 39)
from app.services.summarization import summarize_incident


# ============================================================
# MAIN PIPELINE FUNCTION
# ============================================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    Run the full AI processing pipeline for one incident.

    Called automatically in the background by the FastAPI route handler
    (in incidents.py) after:
      - A new incident is created (POST /incidents)
      - Audio is uploaded to an incident (POST /incidents/{id}/audio)

    Args:
        incident_id:  The database ID of the incident to process
        log_message:  Optional string for extra context in logs
    """

    # Create a timestamp string for all log lines in this run
    # Format "14:22:05" makes it easy to correlate logs with events
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Print a clear separator — each pipeline run is easy to find in terminal
    print(f"[{timestamp}] {'='*60}")
    print(f"[{timestamp}] 🤖 PROCESSING INCIDENT #{incident_id}")
    if log_message:
        print(f"[{timestamp}] Context: {log_message}")
    print(f"[{timestamp}] {'='*60}")


    # ── STEP 1: FETCH INCIDENT FROM DATABASE ─────────────
    print(f"[{timestamp}] 📋 Fetching incident from database...")

    # Build SELECT query: SELECT * FROM incidents WHERE id = incident_id
    select_query = incidents.select().where(incidents.c.id == incident_id)

    # Execute query and get the first (only) matching row
    incident = await database.fetch_one(select_query)

    if not incident:
        # No incident found with this ID — something went wrong upstream
        print(f"[{timestamp}] ❌ Incident #{incident_id} not found!")
        return

    # Convert the database row to a plain Python dict for easier access
    incident = dict(incident)

    print(f"[{timestamp}] ✅ Found: '{incident['description'][:60]}...'")


    # ── STEP 2: TRANSCRIBE AUDIO (REAL — Whisper) ────────
    # If the incident has an audio file, transcribe it to text.
    # The transcript improves both classification and summarization accuracy.

    transcript = None  # Will stay None if no audio was uploaded

    if incident.get("audio_path"):
        print(f"[{timestamp}] 🎤 Transcribing audio: {incident['audio_path']}")
        try:
            # Call Whisper ASR service — may take 5-30 seconds
            transcript = await transcribe_audio(incident["audio_path"])
            print(f"[{timestamp}] ✅ Transcript: '{transcript[:80]}...'")
        except Exception as e:
            # Transcription failed — log and continue (pipeline still runs)
            print(f"[{timestamp}] ⚠️  Transcription failed: {e}")
            # Store error marker so we know transcription was attempted but failed
            transcript = f"[Transcription failed: {str(e)[:100]}]"
    else:
        print(f"[{timestamp}] ℹ️  No audio file — skipping transcription")


    # ── STEP 3: CLASSIFY INCIDENT (REAL — Day 40) ─────────
    # Use zero-shot classification to determine:
    #   - incident_type: "fire", "medical", "crime", "traffic",
    #                    "infrastructure", or "other"
    #   - severity:      "low", "medium", "high", or "critical"
    #
    # Previously this was keyword matching in this file.
    # Now it calls the real classify_incident() service.

    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")

    try:
        # Build the transcript to pass — only pass real text, not error messages
        # If transcript starts with "[", it's an error marker, not real text
        clean_transcript = (
            transcript
            if transcript and not transcript.startswith("[")
            else None
        )

        # Call the classification service
        # Returns: {incident_type, severity, confidence, method, top_scores}
        classification = await classify_incident(
            description=incident["description"],
            transcript=clean_transcript,
        )

        # Extract the fields we need
        incident_type = classification["incident_type"]  # e.g. "fire"
        severity      = classification["severity"]       # e.g. "high"
        confidence    = classification["confidence"]     # e.g. 0.94
        method        = classification["method"]         # "ai" or "keyword_fallback"

        print(f"[{timestamp}] ✅ Classification: type={incident_type}, "
              f"severity={severity}, confidence={confidence:.0%}, method={method}")

    except Exception as e:
        # classify_incident() handles its own fallbacks, so this outer except
        # is a last-resort safety net for truly unexpected errors
        print(f"[{timestamp}] ⚠️  Classification failed unexpectedly: {e}")
        # Use safe defaults so the pipeline can continue
        incident_type = "other"
        severity      = "medium"
        confidence    = 0.0


    # ── STEP 4: SUMMARIZE INCIDENT (REAL — BART) ──────────
    # Generate a clear paragraph summary for the dispatcher.
    # Uses the real BART summarization model from Day 39.

    print(f"[{timestamp}] 📝 Generating AI summary...")

    try:
        # Call the summarization service
        # Passes clean_transcript (real text only, not error messages)
        summary = await summarize_incident(
            description=incident["description"],
            transcript=clean_transcript,
        )
        print(f"[{timestamp}] ✅ Summary: '{summary[:80]}...'")

    except Exception as e:
        # Fallback summary if summarization fails completely
        print(f"[{timestamp}] ⚠️  Summarization failed: {e}")
        summary = f"{incident_type.capitalize()} incident reported. Review description for details."


    # ── STEP 5: CALCULATE RISK SCORE (STUB) ──────────────
    # Numeric score 0.0–1.0 representing urgency.
    # Will be replaced with a real ML model in a future day.
    # For now, derive it from the AI-classified severity.

    print(f"[{timestamp}] ⚠️  Calculating risk score (stub)...")

    # Map severity levels to base risk scores
    severity_to_risk = {
        "critical": 0.95,
        "high":     0.85,
        "medium":   0.55,
        "low":      0.25,
    }

    # Look up base score from severity — default to 0.55 if unknown
    risk_score = severity_to_risk.get(severity, 0.55)

    # Boost score slightly if classification confidence is high
    # A confident high-severity classification is more trustworthy
    if confidence > 0.8 and severity in ("high", "critical"):
        # Small boost — max 0.10 to keep it in range
        risk_score = min(1.0, risk_score + 0.05)

    # Additional keyword-based boost for extreme urgency signals
    text_lower = incident["description"].lower()
    if any(w in text_lower for w in ["trapped", "shots fired", "explosion", "not breathing"]):
        risk_score = min(1.0, risk_score + 0.10)

    print(f"[{timestamp}] ✅ Risk score: {risk_score:.2f}")


    # ── STEP 6: SAVE ALL RESULTS TO DATABASE ─────────────
    # Write all AI-generated fields in one database UPDATE query

    print(f"[{timestamp}] 💾 Saving results to database...")

    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,      # Whisper transcription (or error marker)
            summary=summary,            # BART summary paragraph
            risk_score=risk_score,      # Derived from AI classification
            incident_type=incident_type,# Zero-shot classification result
            severity=severity,          # Severity from classification service
        )
    )

    # Execute the update
    await database.execute(update_query)

    print(f"[{timestamp}] ✅ Database updated")
    print(f"[{timestamp}] 📊 Final: type={incident_type}, severity={severity}, "
          f"risk={risk_score:.2f}, method={method if 'method' in dir() else 'unknown'}")
    print(f"[{timestamp}] 🎉 Pipeline complete for incident #{incident_id}")
    print(f"[{timestamp}] {'='*60}")