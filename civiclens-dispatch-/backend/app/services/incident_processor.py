# backend/app/services/incident_processor.py
# Incident processing pipeline - orchestrates all AI services
# Runs in background after incident is created or updated
#
# Pipeline status as of Day 47 — ALL REAL! NO MORE STUBS!
#   ✅ REAL: Audio transcription (Day 34) - Whisper via Hugging Face
#   ✅ REAL: Text classification (Day 46) - BART-MNLI zero-shot (type + severity)
#   ✅ REAL: Summarization (Day 47) - BART-Large-CNN abstractive summarization
#   ✅ REAL: Risk scoring (Day 45) - BART-MNLI zero-shot (urgency score)
#
# Every single AI service is now powered by a real ML model!

# Import asyncio for async operations
import asyncio

# Import datetime for logging timestamps
from datetime import datetime

# Import database connection for fetching and updating incidents
from app.db.database import database

# Import incidents table definition for building SQL queries
from app.db.models import incidents

# Import ASR service for audio transcription (real since Day 34)
from app.services.asr import transcribe_audio

# Import text classification service (real since Day 46)
from app.services.text_classifier import classify_incident

# Import summarization service (NEW — real since Day 47!)
# summarize_text() sends text to BART-Large-CNN and returns a concise summary
from app.services.summarizer import summarize_text

# Import risk scoring service (real since Day 45)
from app.services.risk_scorer import calculate_risk_score


# ========================================
# MAIN PROCESSING FUNCTION
# ========================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    AI processing pipeline for a single incident.
    
    ALL STEPS ARE NOW REAL ML — NO STUBS REMAINING!
    
    1. Fetch incident from database
    2. Transcribe audio (if present) → transcript          ← REAL (Day 34)
    3. Classify text → incident_type, severity             ← REAL (Day 46)
    4. Summarize description + transcript → summary        ← REAL (Day 47!)
    5. Calculate risk score → risk_score                   ← REAL (Day 45)
    6. Update database with all AI-generated fields
    
    If any individual step fails, the pipeline continues with remaining steps.
    
    Args:
        incident_id: The database ID of the incident to process
        log_message: Optional message to print for debugging
    """
    
    # Get current timestamp for consistent logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the start of processing
    print(f"\n[{timestamp}] {'=' * 60}")
    print(f"[{timestamp}] 🤖 Processing incident {incident_id}")
    
    if log_message:
        print(f"[{timestamp}] 📋 {log_message}")
    
    
    # ========================================
    # STEP 1: Fetch Incident from Database
    # ========================================
    
    print(f"[{timestamp}] 📥 Fetching incident {incident_id} from database...")
    
    # Build SELECT query to get the incident by ID
    query = incidents.select().where(incidents.c.id == incident_id)
    
    # Execute and get the result
    incident = await database.fetch_one(query)
    
    # Check if incident exists
    if not incident:
        print(f"[{timestamp}] ❌ Incident {incident_id} not found in database")
        return
    
    print(f"[{timestamp}] 📥 Fetched: {incident['description'][:60]}...")
    
    
    # ========================================
    # STEP 2: Audio Transcription (REAL — Day 34)
    # ========================================
    
    transcript = None
    
    if incident["audio_path"]:
        print(f"[{timestamp}] 🎤 Audio file found: {incident['audio_path']}")
        print(f"[{timestamp}] 🎤 Starting transcription...")
        
        try:
            transcript = await transcribe_audio(incident["audio_path"])
            print(f"[{timestamp}] ✅ Transcription complete")
            print(f"[{timestamp}] 📝 Transcript: {transcript[:100]}...")
        except Exception as e:
            print(f"[{timestamp}] ⚠️  Transcription failed: {str(e)}")
            transcript = f"[Transcription failed: {str(e)}]"
    else:
        print(f"[{timestamp}] ℹ️  No audio file — skipping transcription")
    
    
    # ========================================
    # STEP 3: Text Classification (REAL — Day 46)
    # ========================================
    
    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")
    print(f"[{timestamp}] 🔮 Calling Hugging Face zero-shot classification (2 passes)...")
    
    # Combine description and transcript for classification
    classify_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        classify_text += " " + transcript
    
    try:
        classification = await classify_incident(classify_text)
        incident_type = classification["incident_type"]
        severity = classification["severity"]
        classify_method = classification["method"]
        type_conf = classification["type_confidence"]
        severity_conf = classification["severity_confidence"]
        
        print(f"[{timestamp}] ✅ Classified as: {incident_type} ({severity} severity) [via {classify_method}]")
        print(f"[{timestamp}]    Type confidence: {type_conf:.2f}, Severity confidence: {severity_conf:.2f}")
    except Exception as e:
        print(f"[{timestamp}] ❌ Classification error: {str(e)}")
        incident_type = "other"
        severity = "medium"
    
    
    # ========================================
    # STEP 4: Summarization (REAL — Day 47!)
    # ========================================
    
    print(f"[{timestamp}] 📝 Generating summary...")
    print(f"[{timestamp}] 🔮 Calling Hugging Face BART-Large-CNN summarization...")
    
    # Combine description and transcript for a richer summary
    # The summarizer works best with more context
    summary_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        summary_text += " " + transcript
    
    try:
        # Call the REAL summarization service
        # This sends text to facebook/bart-large-cnn and gets back a generated summary
        summary_result = await summarize_text(summary_text)
        
        summary = summary_result["summary"]
        summary_method = summary_result["method"]
        in_len = summary_result["input_length"]
        out_len = summary_result["output_length"]
        
        print(f"[{timestamp}] ✅ Summary generated (via {summary_method}): {summary[:100]}...")
        print(f"[{timestamp}]    Input: {in_len} chars → Output: {out_len} chars")
    
    except Exception as e:
        # Last resort fallback — truncate the description
        print(f"[{timestamp}] ❌ Summarization error: {str(e)}")
        print(f"[{timestamp}] ⚠️  Using truncated description as summary")
        summary = incident["description"][:150] + "..." if len(incident["description"]) > 150 else incident["description"]
    
    
    # ========================================
    # STEP 5: Risk Scoring (REAL — Day 45)
    # ========================================
    
    print(f"[{timestamp}] ⚠️  Calculating risk score...")
    print(f"[{timestamp}] 🔮 Calling Hugging Face zero-shot classification...")
    
    risk_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        risk_text += " " + transcript
    
    try:
        risk_result = await calculate_risk_score(risk_text)
        risk_score = risk_result["score"]
        scoring_method = risk_result["method"]
        
        print(f"[{timestamp}] ✅ Risk score: {risk_score:.4f} (via {scoring_method})")
        
        if risk_result.get("labels"):
            for label, confidence in risk_result["labels"].items():
                print(f"[{timestamp}]    {confidence:.3f} → {label}")
    except Exception as e:
        print(f"[{timestamp}] ❌ Risk scoring error: {str(e)}")
        severity_defaults = {"high": 0.8, "medium": 0.5, "low": 0.2}
        risk_score = severity_defaults.get(severity, 0.5)
        print(f"[{timestamp}] ⚠️  Default risk score: {risk_score}")
    
    
    # ========================================
    # STEP 6: Update Database with All AI Results
    # ========================================
    
    print(f"[{timestamp}] 💾 Saving AI results to database...")
    
    # Build UPDATE query — writes ALL AI-generated fields at once
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,           # REAL from Whisper ASR (Day 34)
            incident_type=incident_type,    # REAL from BART-MNLI (Day 46)
            severity=severity,              # REAL from BART-MNLI (Day 46)
            summary=summary,                # REAL from BART-Large-CNN (Day 47)
            risk_score=risk_score,          # REAL from BART-MNLI (Day 45)
        )
    )
    
    # Execute the update
    await database.execute(update_query)
    
    # Log completion
    print(f"[{timestamp}] ✅ Processing complete for incident {incident_id}")
    print(f"[{timestamp}] {'=' * 60}")


# ========================================
# IMPLEMENTATION STATUS (Day 47) — ALL REAL!
# ========================================

# ✅ REAL: Audio transcription (Day 34) - Whisper via Hugging Face
# ✅ REAL: Text classification (Day 46) - BART-MNLI zero-shot (type + severity)
# ✅ REAL: Summarization (Day 47) - BART-Large-CNN abstractive summarization
# ✅ REAL: Risk scoring (Day 45) - BART-MNLI zero-shot (urgency score)
#
# 🎉 NO MORE STUBS! The entire AI pipeline is real!
#
# Models used:
#   - openai/whisper-base (ASR)
#   - facebook/bart-large-mnli (classification + risk scoring)
#   - facebook/bart-large-cnn (summarization)