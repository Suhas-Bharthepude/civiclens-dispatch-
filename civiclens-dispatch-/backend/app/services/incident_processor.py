# backend/app/services/incident_processor.py
#
# Incident Processing Pipeline — orchestrates all AI services.
# Runs in the background after an incident is created or a file is uploaded.
#
# AI pipeline status as of Day 42:
#   ✅ Step 1: Fetch incident from database
#   ✅ Step 2: Transcribe audio  (Whisper via Hugging Face)
#   ✅ Step 3: Classify type/severity (BART zero-shot)
#   ✅ Step 3.5: Analyze image (BLIP captioning) ← NEW DAY 42
#   ✅ Step 4: Summarize incident (BART-CNN)
#   🔄 Step 5: Calculate risk score (rule-based stub)
#   ✅ Step 6: Save all AI results to database

import asyncio
from datetime import datetime

from app.db.database import database
from app.db.models import incidents

# Whisper ASR: audio → transcript text
from app.services.asr import transcribe_audio

# BART zero-shot: text → incident_type + severity
from app.services.classification import classify_incident

# BLIP: image → description text (NEW Day 42)
from app.services.image_analysis import analyze_image

# BART-CNN: text → summary paragraph
from app.services.summarization import summarize_incident


# ============================================================
# MAIN PIPELINE FUNCTION
# ============================================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    Run the full AI processing pipeline for one incident.

    Called automatically in the background by incidents.py after:
      - A new incident is created (POST /incidents)
      - Audio is uploaded  (POST /incidents/{id}/audio)
      - Image is uploaded  (POST /incidents/{id}/image)

    Args:
        incident_id:  The database ID of the incident to process
        log_message:  Optional context string for logs
    """

    # Timestamp for all log lines in this run
    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] {'='*60}")
    print(f"[{timestamp}] 🤖 PROCESSING INCIDENT #{incident_id}")
    if log_message:
        print(f"[{timestamp}] Context: {log_message}")
    print(f"[{timestamp}] {'='*60}")


    # ── STEP 1: FETCH INCIDENT ────────────────────────────
    print(f"[{timestamp}] 📋 Fetching incident from database...")

    select_query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(select_query)

    if not incident:
        print(f"[{timestamp}] ❌ Incident #{incident_id} not found!")
        return

    # Convert database row to a plain Python dict
    incident = dict(incident)
    print(f"[{timestamp}] ✅ Found: '{incident['description'][:60]}...'")


    # ── STEP 2: TRANSCRIBE AUDIO ──────────────────────────
    # Whisper converts the uploaded audio file to text.
    # The transcript improves classification and summarization.
    transcript = None

    if incident.get("audio_path"):
        print(f"[{timestamp}] 🎤 Transcribing audio...")
        try:
            transcript = await transcribe_audio(incident["audio_path"])
            print(f"[{timestamp}] ✅ Transcript: '{transcript[:80]}...'")
        except Exception as e:
            print(f"[{timestamp}] ⚠️  Transcription failed: {e}")
            transcript = f"[Transcription failed: {str(e)[:100]}]"
    else:
        print(f"[{timestamp}] ℹ️  No audio file — skipping transcription")

    # Build a "clean" transcript — only real text, not error markers
    # Error markers start with "[" (e.g., "[Transcription failed: ...]")
    clean_transcript = (
        transcript
        if transcript and not transcript.startswith("[")
        else None
    )


    # ── STEP 3: CLASSIFY INCIDENT ─────────────────────────
    # Zero-shot classification determines incident type and severity.
    print(f"[{timestamp}] 🏷️  Classifying incident...")

    try:
        classification = await classify_incident(
            description=incident["description"],
            transcript=clean_transcript,
        )
        incident_type = classification["incident_type"]
        severity      = classification["severity"]
        confidence    = classification["confidence"]
        method        = classification["method"]
        print(f"[{timestamp}] ✅ type={incident_type}, severity={severity}, "
              f"confidence={confidence:.0%}, method={method}")

    except Exception as e:
        print(f"[{timestamp}] ⚠️  Classification failed: {e}")
        incident_type = "other"
        severity      = "medium"
        confidence    = 0.0


    # ── STEP 3.5: ANALYZE IMAGE ───────────────────────────  ← NEW DAY 42
    # BLIP generates a text description of the uploaded photo.
    # The description is stored in image_description and shown in the UI.
    image_description = None

    if incident.get("image_path"):
        print(f"[{timestamp}] 📸 Analyzing image: {incident['image_path']}")
        try:
            # Call the BLIP image captioning service
            image_description = await analyze_image(incident["image_path"])
            print(f"[{timestamp}] ✅ Image description: '{image_description[:80]}...'")

        except Exception as e:
            # Image analysis failure doesn't stop the pipeline
            print(f"[{timestamp}] ⚠️  Image analysis failed: {e}")
            image_description = "Image analysis unavailable — manual review recommended."
    else:
        print(f"[{timestamp}] ℹ️  No image file — skipping image analysis")


    # ── STEP 4: SUMMARIZE INCIDENT ────────────────────────
    # BART generates a paragraph summary combining text + transcript.
    # (Image description could be incorporated here in future days)
    print(f"[{timestamp}] 📝 Generating summary...")

    try:
        summary = await summarize_incident(
            description=incident["description"],
            transcript=clean_transcript,
        )
        print(f"[{timestamp}] ✅ Summary: '{summary[:80]}...'")

    except Exception as e:
        print(f"[{timestamp}] ⚠️  Summarization failed: {e}")
        summary = f"{incident_type.capitalize()} incident. Review description for details."


    # ── STEP 5: CALCULATE RISK SCORE ─────────────────────
    # Rule-based stub — will be replaced with ML model later
    print(f"[{timestamp}] ⚠️  Calculating risk score (stub)...")

    severity_to_risk = {
        "critical": 0.95,
        "high":     0.85,
        "medium":   0.55,
        "low":      0.25,
    }

    risk_score = severity_to_risk.get(severity, 0.55)

    # Boost if high-confidence classification
    if confidence > 0.8 and severity in ("high", "critical"):
        risk_score = min(1.0, risk_score + 0.05)

    # Boost for extreme urgency keywords
    text_lower = incident["description"].lower()
    if any(w in text_lower for w in ["trapped", "shots fired", "explosion", "not breathing"]):
        risk_score = min(1.0, risk_score + 0.10)

    # Also consider image description for risk boost
    # If the image description mentions dangerous conditions, boost the score
    if image_description:
        img_lower = image_description.lower()
        if any(w in img_lower for w in ["fire", "flames", "smoke", "crash", "damage", "injured"]):
            risk_score = min(1.0, risk_score + 0.05)

    print(f"[{timestamp}] ✅ Risk score: {risk_score:.2f}")


    # ── STEP 6: SAVE ALL RESULTS ──────────────────────────
    # Write all AI-generated fields in one database UPDATE
    print(f"[{timestamp}] 💾 Saving results to database...")


    update_values = dict(
        transcript=transcript,
        summary=summary,
        risk_score=risk_score,
        incident_type=incident_type,
        severity=severity,
    )
    if image_description is not None:
        update_values["image_description"] = image_description

    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(**update_values)
    )


    await database.execute(update_query)

    print(f"[{timestamp}] ✅ Database updated")
    print(f"[{timestamp}] 📊 type={incident_type}, severity={severity}, "
          f"risk={risk_score:.2f}, "
          f"has_image_desc={image_description is not None}")
    print(f"[{timestamp}] 🎉 Pipeline complete for incident #{incident_id}")
    print(f"[{timestamp}] {'='*60}")