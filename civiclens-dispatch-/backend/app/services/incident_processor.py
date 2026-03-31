# backend/app/services/incident_processor.py
# Incident processing pipeline - orchestrates all AI services
# Runs in background after incident is created or updated
#
# Pipeline status as of Day 45:
#   ✅ REAL: Audio transcription (Day 34) - Whisper via Hugging Face
#   ✅ REAL: Risk scoring (Day 45) - BART-MNLI zero-shot classification
#   🚧 STUB: Text classification (incident_type, severity) - keyword-based
#   🚧 STUB: Summarization - template-based
#
# Each stub will be replaced with real models in upcoming days.

# Import asyncio for simulating delays in stub functions
# and for async sleep during processing
import asyncio

# Import datetime for logging timestamps on each processing step
# Timestamps help debug timing issues and track processing duration
from datetime import datetime

# Import database connection object
# This is the async database connection we set up on Day 10
# Used to fetch and update incident records
from app.db.database import database

# Import incidents table definition
# This is the SQLAlchemy table object that represents the incidents table
# Used to build SELECT and UPDATE queries
from app.db.models import incidents

# Import ASR service for audio transcription (real since Day 34)
# transcribe_audio() sends audio to Whisper model via Hugging Face API
# Returns the text transcript of the audio
from app.services.asr import transcribe_audio

# Import risk scoring service (NEW - real since Day 45)
# calculate_risk_score() sends text to BART-MNLI via Hugging Face API
# Returns a dict with 'score' (0.0-1.0), 'labels', and 'method'
from app.services.risk_scorer import calculate_risk_score


# ========================================
# MAIN PROCESSING FUNCTION
# ========================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    AI processing pipeline for a single incident.
    
    This function orchestrates all AI services in sequence:
    1. Fetch incident from database
    2. Transcribe audio (if present) → transcript          ← REAL (Day 34)
    3. Classify text → incident_type, severity             ← STUB (keyword-based)
    4. Summarize description + transcript → summary        ← STUB (template-based)
    5. Calculate risk score → risk_score                   ← REAL (Day 45!)
    6. Update database with all AI-generated fields
    
    Runs asynchronously in background after incident creation.
    If any individual step fails, the pipeline continues with remaining steps.
    
    Args:
        incident_id: The database ID of the incident to process
        log_message: Optional message to print (for debugging)
    """
    
    # Get current timestamp for logging
    # We use this to track when each step starts and finishes
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the start of processing
    print(f"\n[{timestamp}] {'=' * 60}")
    print(f"[{timestamp}] 🤖 Processing incident {incident_id}")
    
    # Print optional log message if provided
    if log_message:
        print(f"[{timestamp}] 📋 {log_message}")
    
    
    # ========================================
    # STEP 1: Fetch Incident from Database
    # ========================================
    
    print(f"[{timestamp}] 📥 Fetching incident {incident_id} from database...")
    
    # Build a SELECT query to get the incident by its ID
    # incidents.select() creates a SELECT * FROM incidents query
    # .where() adds the WHERE clause to filter by ID
    query = incidents.select().where(incidents.c.id == incident_id)
    
    # Execute the query and get the result
    # await pauses here until the database responds
    incident = await database.fetch_one(query)
    
    # Check if the incident exists
    # It might have been deleted between creation and processing
    if not incident:
        print(f"[{timestamp}] ❌ Incident {incident_id} not found in database")
        return
    
    print(f"[{timestamp}] 📥 Fetched incident {incident_id}: {incident['description'][:60]}...")
    
    
    # ========================================
    # STEP 2: Audio Transcription (REAL - Day 34)
    # ========================================
    
    # Initialize transcript as None (will be set if audio exists)
    transcript = None
    
    # Check if incident has an audio file attached
    # audio_path is set when the user uploads an audio file
    # Could be None if no audio was uploaded with this incident
    if incident["audio_path"]:
        # Audio exists - transcribe it using the real Whisper model
        print(f"[{timestamp}] 🎤 Audio file found: {incident['audio_path']}")
        print(f"[{timestamp}] 🎤 Starting transcription...")
        
        try:
            # Call ASR service to transcribe audio
            # This sends the audio to Whisper via Hugging Face API
            # await pauses here until transcription completes (5-30 seconds)
            transcript = await transcribe_audio(incident["audio_path"])
            
            # Log successful transcription (show first 100 chars)
            print(f"[{timestamp}] ✅ Transcription complete")
            print(f"[{timestamp}] 📝 Transcript: {transcript[:100]}...")
            
        except Exception as e:
            # Transcription failed - log error but continue with other steps
            # The pipeline shouldn't stop just because transcription failed
            print(f"[{timestamp}] ⚠️  Transcription failed: {str(e)}")
            print(f"[{timestamp}] ⚠️  Continuing with other AI tasks...")
            
            # Set transcript to error message so we know it failed
            transcript = f"[Transcription failed: {str(e)}]"
    else:
        # No audio file attached to this incident
        print(f"[{timestamp}] ℹ️  No audio file - skipping transcription")
    
    
    # ========================================
    # STEP 3: Text Classification (STUB - keyword-based)
    # ========================================
    
    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")
    
    # Simulate a small processing delay (stubs should still feel realistic)
    await asyncio.sleep(0.5)
    
    # Combine description and transcript for classification
    # Using both gives the classifier more text to work with
    description_lower = incident["description"].lower()
    
    # Build the full text to classify
    # Include transcript if it exists and isn't an error message
    text_to_classify = description_lower
    if transcript and not transcript.startswith("[Transcription failed"):
        # Append the transcript to give the classifier more context
        text_to_classify += " " + transcript.lower()
    
    # Simple keyword-based classification (STUB)
    # This will be replaced with a real NLP model in a future day
    # For now, we check for keywords that indicate incident type
    if "fire" in text_to_classify or "smoke" in text_to_classify or "burn" in text_to_classify:
        incident_type = "fire"
        severity = "high"
    elif "medical" in text_to_classify or "injured" in text_to_classify or "hurt" in text_to_classify:
        incident_type = "medical"
        severity = "high"
    elif "accident" in text_to_classify or "crash" in text_to_classify or "collision" in text_to_classify:
        incident_type = "traffic"
        severity = "medium"
    elif "noise" in text_to_classify or "complaint" in text_to_classify or "loud" in text_to_classify:
        incident_type = "noise"
        severity = "low"
    elif "break" in text_to_classify or "robbery" in text_to_classify or "theft" in text_to_classify or "steal" in text_to_classify:
        incident_type = "crime"
        severity = "high"
    elif "water" in text_to_classify or "flood" in text_to_classify or "leak" in text_to_classify:
        incident_type = "infrastructure"
        severity = "medium"
    else:
        # Default if no keywords match
        incident_type = "other"
        severity = "medium"
    
    print(f"[{timestamp}] ✅ Classified as: {incident_type} ({severity} severity)")
    
    
    # ========================================
    # STEP 4: Summarization (STUB - template-based)
    # ========================================
    
    print(f"[{timestamp}] 📝 Generating summary...")
    
    # Simulate a small processing delay
    await asyncio.sleep(0.5)
    
    # Generate summary combining description and transcript
    # This is placeholder logic - will be replaced with a real summarization model
    if transcript and not transcript.startswith("[Transcription failed"):
        # Have transcript - create a richer summary that mentions both sources
        summary = (
            f"{incident_type.capitalize()} incident. "
            f"{incident['description'][:50]}... "
            f"Audio transcript available. "
            f"Caller reported distress."
        )
    else:
        # No transcript - summary is just based on the description
        summary = f"{incident_type.capitalize()} incident: {incident['description'][:80]}..."
    
    print(f"[{timestamp}] ✅ Summary generated: {summary[:80]}...")
    
    
    # ========================================
    # STEP 5: Risk Scoring (REAL - Day 45!)
    # ========================================
    
    print(f"[{timestamp}] ⚠️  Calculating risk score...")
    print(f"[{timestamp}] 🔮 Calling Hugging Face zero-shot classification...")
    
    # Build the full text for risk scoring
    # Combine description and transcript (if available) for best accuracy
    # The more context the model has, the better it can assess urgency
    risk_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        # Add transcript to give the model more context about the situation
        risk_text += " " + transcript
    
    try:
        # Call the REAL risk scoring service
        # This sends the text to facebook/bart-large-mnli via Hugging Face API
        # The model classifies the text into urgency categories
        # Then we convert those into a 0.0-1.0 risk score
        risk_result = await calculate_risk_score(risk_text)
        
        # Extract the score from the result dictionary
        risk_score = risk_result["score"]
        
        # Log the result including which method was used (ml or fallback)
        scoring_method = risk_result["method"]
        print(f"[{timestamp}] ✅ Risk score: {risk_score:.4f} (via {scoring_method})")
        
        # Log label confidences if ML method was used
        if risk_result.get("labels"):
            for label, confidence in risk_result["labels"].items():
                print(f"[{timestamp}]    {confidence:.3f} → {label}")
    
    except Exception as e:
        # Risk scoring completely failed - use a basic default
        # This is a last resort - the calculate_risk_score function
        # already has its own fallback, so this rarely triggers
        print(f"[{timestamp}] ❌ Risk scoring error: {str(e)}")
        print(f"[{timestamp}] ⚠️  Using default score based on severity")
        
        # Assign a default score based on the classified severity
        severity_defaults = {"high": 0.8, "medium": 0.5, "low": 0.2}
        risk_score = severity_defaults.get(severity, 0.5)
        print(f"[{timestamp}] ⚠️  Default risk score: {risk_score}")
    
    
    # ========================================
    # STEP 6: Update Database with All AI Results
    # ========================================
    
    print(f"[{timestamp}] 💾 Saving AI results to database...")
    
    # Build the UPDATE query
    # This updates the incident row with all AI-generated fields at once
    # Doing it in one query is more efficient and atomic than multiple queries
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,           # REAL from Whisper ASR (Day 34)
            summary=summary,                 # Stub template-based
            risk_score=risk_score,          # REAL from BART-MNLI (Day 45)
            incident_type=incident_type,    # Stub keyword-based
            severity=severity               # Stub keyword-based
        )
    )
    
    # Execute the update query
    # This writes all the AI-generated data to the database in one operation
    await database.execute(update_query)
    
    # Log completion
    print(f"[{timestamp}] ✅ Processing complete for incident {incident_id}")
    print(f"[{timestamp}] {'=' * 60}")


# ========================================
# IMPLEMENTATION STATUS (Day 45)
# ========================================

# ✅ REAL: Audio transcription (Day 34) - Whisper via Hugging Face
# ✅ REAL: Risk scoring (Day 45) - BART-MNLI zero-shot classification
# 🚧 STUB: Text classification (incident_type + severity) - keyword-based
# 🚧 STUB: Summarization - template-based
#
# Next to replace:
#   - Text classification with real NLP model
#   - Summarization with real model