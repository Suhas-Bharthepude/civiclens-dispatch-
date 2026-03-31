# backend/app/services/incident_processor.py
# Incident processing pipeline - orchestrates all AI services
# Runs in background after incident is created or updated
# Day 34: Now uses REAL ASR transcription (or mock)

# Import asyncio for simulating delays and async operations
import asyncio

# Import datetime for logging timestamps
from datetime import datetime

# Import database connection
from app.db.database import database

# Import incidents table for database operations
from app.db.models import incidents

# Import ASR service for audio transcription
# This is the real AI integration!
from app.services.asr import transcribe_audio


# ========================================
# MAIN PROCESSING FUNCTION
# ========================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    AI processing pipeline for a single incident.
    
    This function orchestrates all AI services:
    1. Fetch incident from database
    2. Transcribe audio (if present) → transcript ← REAL NOW!
    3. Classify text → incident_type, severity (still stub)
    4. Summarize description + transcript → summary (still stub)
    5. Calculate risk score → risk_score (still stub)
    6. Update database with all AI-generated fields
    
    Runs asynchronously in background after incident creation.
    
    Args:
        incident_id: ID of incident to process
        log_message: Optional custom log message for debugging
    
    Returns:
        None (updates database directly)
    
    Example:
        await process_incident(5)
        # Incident #5 is now processed with AI-generated fields
    """
    
    # ========================================
    # LOGGING SETUP
    # ========================================
    
    # Create timestamp for all log messages
    # Format: "2024-03-26 14:30:45"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log start of processing
    if log_message:
        print(f"[{timestamp}] {log_message}")
    else:
        print(f"[{timestamp}] Starting AI processing for incident {incident_id}")
    
    
    # ========================================
    # STEP 1: Fetch incident from database
    # ========================================
    
    # Build SELECT query for this specific incident
    # incidents.select() creates a query
    # .where() filters to only this incident ID
    query = incidents.select().where(incidents.c.id == incident_id)
    
    # Execute query and get result
    # fetch_one returns a single row or None
    incident = await database.fetch_one(query)
    
    # Check if incident exists
    if incident is None:
        # Incident not found - log error and exit
        print(f"[{timestamp}] ❌ Incident {incident_id} not found - aborting")
        return
    
    # Log successful fetch
    print(f"[{timestamp}] 📥 Fetched incident {incident_id}")
    
    
    # ========================================
    # STEP 2: Audio Transcription (REAL AI!)
    # ========================================
    
    # Initialize transcript as None (will be set if audio exists)
    transcript = None
    
    # Check if incident has audio file
    # incident["audio_path"] is the path to uploaded audio file
    # Could be None if no audio was uploaded
    if incident["audio_path"]:
        # Audio exists - transcribe it!
        print(f"[{timestamp}] 🎤 Audio file found: {incident['audio_path']}")
        print(f"[{timestamp}] 🎤 Starting transcription...")
        
        try:
            # Call ASR service to transcribe audio
            # This is the REAL AI call (or mock if USE_MOCK_TRANSCRIPTION=True)
            # await pauses here until transcription completes
            # This can take 5-30 seconds depending on audio length
            transcript = await transcribe_audio(incident["audio_path"])
            
            # Log successful transcription
            print(f"[{timestamp}] ✅ Transcription complete")
            print(f"[{timestamp}] 📝 Transcript: {transcript[:100]}...")
            
        except Exception as e:
            # Transcription failed - log error but continue processing
            # Don't fail entire pipeline if just transcription fails
            print(f"[{timestamp}] ⚠️  Transcription failed: {str(e)}")
            print(f"[{timestamp}] ⚠️  Continuing with other AI tasks...")
            
            # Set transcript to error message so we know it failed
            transcript = f"[Transcription failed: {str(e)}]"
    else:
        # No audio file - skip transcription
        print(f"[{timestamp}] ℹ️  No audio file - skipping transcription")
    
    
    # ========================================
    # STEP 3: Text Classification (STUB - still fake)
    # ========================================
    
    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")
    
    # Simulate AI processing time
    await asyncio.sleep(1)
    
    # Get description text for classification
    # If we have transcript, we could include it in classification (future)
    # For now, just use description
    description_lower = incident["description"].lower()
    
    # Also check transcript if available
    text_to_classify = description_lower
    if transcript and not transcript.startswith("[Transcription failed"):
        # Have valid transcript - include it in classification
        text_to_classify += " " + transcript.lower()
    
    # Simple keyword-based classification (STUB - will be replaced with real model)
    # This is placeholder logic until we integrate real NLP model (Days 44-45)
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
        incident_type = "other"
        severity = "medium"
    
    print(f"[{timestamp}] ✅ Classified as: {incident_type} ({severity} severity)")
    
    
    # ========================================
    # STEP 4: Summarization (STUB - still fake)
    # ========================================
    
    print(f"[{timestamp}] 📝 Generating summary...")
    
    # Simulate AI processing time
    await asyncio.sleep(1)
    
    # Generate summary combining description and transcript
    # This is placeholder logic - real summarization model in Days 38-39
    if transcript and not transcript.startswith("[Transcription failed"):
        # Have transcript - create richer summary
        summary = (
            f"{incident_type.capitalize()} incident. "
            f"{incident['description'][:50]}... "
            f"Audio transcript available. "
            f"Caller reported distress."
        )
    else:
        # No transcript - just use description
        summary = f"{incident_type.capitalize()} incident: {incident['description'][:80]}..."
    
    print(f"[{timestamp}] ✅ Summary generated: {summary[:80]}...")
    
    
    # ========================================
    # STEP 5: Risk Scoring (STUB - still fake)
    # ========================================
    
    print(f"[{timestamp}] ⚠️  Calculating risk score...")
    
    # Simulate AI processing time
    await asyncio.sleep(1)
    
    # Simple rule-based risk score (STUB - will be replaced with ML model)
    # This is placeholder logic until we build real risk scoring model (Days 45-47)
    
    # Base score from severity
    if severity == "high":
        risk_score = 0.85
    elif severity == "medium":
        risk_score = 0.55
    else:
        risk_score = 0.25
    
    # Boost score if certain keywords present in description
    if "emergency" in description_lower or "urgent" in description_lower:
        risk_score = min(1.0, risk_score + 0.15)
    
    # Boost score if transcript indicates distress (if we have valid transcript)
    if transcript and not transcript.startswith("[Transcription failed"):
        # Check transcript for distress indicators
        transcript_lower = transcript.lower()
        if "distress" in transcript_lower or "help" in transcript_lower or "emergency" in transcript_lower:
            risk_score = min(1.0, risk_score + 0.10)
        
        # Check for injury/danger words
        if "injured" in transcript_lower or "hurt" in transcript_lower or "bleeding" in transcript_lower:
            risk_score = min(1.0, risk_score + 0.10)
    
    # Ensure risk_score stays in 0.0-1.0 range
    risk_score = max(0.0, min(1.0, risk_score))
    
    print(f"[{timestamp}] ✅ Risk score: {risk_score:.2f}")
    
    
    # ========================================
    # STEP 6: Update Database with All AI Results
    # ========================================
    
    print(f"[{timestamp}] 💾 Saving AI results to database...")
    
    # Build UPDATE query
    # This updates the incident row with all AI-generated fields
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,           # REAL transcription from ASR
            summary=summary,                 # Stub summary
            risk_score=risk_score,          # Stub risk score
            incident_type=incident_type,    # Stub classification
            severity=severity               # Stub classification
        )
    )
    
    # Execute the update query
    # This writes all the AI-generated data to the database
    await database.execute(update_query)
    
    # Log completion
    print(f"[{timestamp}] ✅ Processing complete for incident {incident_id}")
    print(f"[{timestamp}] " + "="*60)


# ========================================
# NOTES FOR FUTURE DAYS
# ========================================

# This is a HYBRID implementation as of Day 34:
#
# ✅ REAL: Audio transcription (Day 34)
# 🚧 STUB: Text classification (will implement Days 44-45)
# 🚧 STUB: Summarization (will implement Days 38-39)
# 🚧 STUB: Risk scoring (will implement Days 45-47)
# 🚧 STUB: Image analysis (will implement Days 42-43)
#
# The pipeline architecture is solid and ready for more AI models.
# Each stub will be replaced with real models in upcoming days.