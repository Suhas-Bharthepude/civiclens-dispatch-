# backend/app/services/incident_processor.py
# Incident processing pipeline - orchestrates all AI services
# Runs in background after incident is created or updated
#
# Pipeline status as of Day 48 — FULLY MULTIMODAL!
#   ✅ REAL: Audio transcription (Day 34) - Whisper via Hugging Face
#   ✅ REAL: Text classification (Day 46) - BART-MNLI zero-shot (type + severity)
#   ✅ REAL: Summarization (Day 47) - BART-Large-CNN abstractive summarization
#   ✅ REAL: Risk scoring (Day 45) - BART-MNLI zero-shot (urgency score)
#   ✅ REAL: Image analysis (Day 48) - BLIP image captioning  ← NEW!
#
# Three modalities: Audio + Text + Images

# Import asyncio for async operations
import asyncio

# Import datetime for logging timestamps
from datetime import datetime

# Import database connection
from app.db.database import database

# Import incidents table definition
from app.db.models import incidents

# Import ASR service (real since Day 34)
from app.services.asr import transcribe_audio

# Import text classification service (real since Day 46)
from app.services.text_classifier import classify_incident

# Import summarization service (real since Day 47)
from app.services.summarizer import summarize_text

# Import risk scoring service (real since Day 45)
from app.services.risk_scorer import calculate_risk_score

# Import image analysis service (NEW — real since Day 48!)
# analyze_image() sends image bytes to BLIP and returns a text caption
from app.services.image_analyzer import analyze_image


# ========================================
# MAIN PROCESSING FUNCTION
# ========================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    AI processing pipeline for a single incident.
    
    FULLY MULTIMODAL — processes audio, text, AND images!
    
    1. Fetch incident from database
    2. Transcribe audio (if present) → transcript          ← REAL (Day 34)
    3. Analyze image (if present) → image_caption          ← REAL (Day 48!) NEW
    4. Classify text → incident_type, severity             ← REAL (Day 46)
    5. Summarize description + transcript → summary        ← REAL (Day 47)
    6. Calculate risk score → risk_score                   ← REAL (Day 45)
    7. Update database with all AI-generated fields
    
    If any individual step fails, the pipeline continues with remaining steps.
    """
    
    # Get current timestamp for logging
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"\n[{timestamp}] {'=' * 60}")
    print(f"[{timestamp}] 🤖 Processing incident {incident_id}")
    
    if log_message:
        print(f"[{timestamp}] 📋 {log_message}")
    
    
    # ========================================
    # STEP 1: Fetch Incident from Database
    # ========================================
    
    print(f"[{timestamp}] 📥 Fetching incident {incident_id} from database...")
    
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)
    
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
    # STEP 3: Image Analysis (REAL — Day 48!) NEW
    # ========================================
    
    image_caption = None
    
    # Check if incident has an image file attached
    if incident["image_path"]:
        print(f"[{timestamp}] 🖼️  Image file found: {incident['image_path']}")
        print(f"[{timestamp}] 🖼️  Analyzing image with BLIP model...")
        
        try:
            # Call the BLIP image captioning model
            # This sends the image bytes to Hugging Face and gets a text description
            image_result = await analyze_image(incident["image_path"])
            
            image_caption = image_result["caption"]
            image_method = image_result["method"]
            
            print(f"[{timestamp}] ✅ Image caption (via {image_method}): {image_caption}")
        
        except Exception as e:
            print(f"[{timestamp}] ⚠️  Image analysis failed: {str(e)}")
            image_caption = f"[Image analysis failed: {str(e)}]"
    else:
        print(f"[{timestamp}] ℹ️  No image file — skipping image analysis")
    
    
    # ========================================
    # STEP 4: Text Classification (REAL — Day 46)
    # ========================================
    
    print(f"[{timestamp}] 🏷️  Classifying incident type and severity...")
    
    # Combine description, transcript, and image caption for classification
    # More context = better classification
    classify_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        classify_text += " " + transcript
    if image_caption and not image_caption.startswith("["):
        # Include the image caption in classification for additional context
        # e.g., if image shows "a burning building" that helps classify as fire
        classify_text += " Image shows: " + image_caption
    
    try:
        classification = await classify_incident(classify_text)
        incident_type = classification["incident_type"]
        severity = classification["severity"]
        classify_method = classification["method"]
        
        print(f"[{timestamp}] ✅ Classified as: {incident_type} ({severity} severity) [via {classify_method}]")
    except Exception as e:
        print(f"[{timestamp}] ❌ Classification error: {str(e)}")
        incident_type = "other"
        severity = "medium"
    
    
    # ========================================
    # STEP 5: Summarization (REAL — Day 47)
    # ========================================
    
    print(f"[{timestamp}] 📝 Generating summary...")
    
    # Combine all available text sources for the richest possible summary
    summary_input = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        summary_input += " " + transcript
    if image_caption and not image_caption.startswith("["):
        summary_input += " Visual observation: " + image_caption
    
    try:
        summary_result = await summarize_text(summary_input)
        summary = summary_result["summary"]
        summary_method = summary_result["method"]
        
        print(f"[{timestamp}] ✅ Summary (via {summary_method}): {summary[:100]}...")
    except Exception as e:
        print(f"[{timestamp}] ❌ Summarization error: {str(e)}")
        summary = incident["description"][:150] + "..." if len(incident["description"]) > 150 else incident["description"]
    
    
    # ========================================
    # STEP 6: Risk Scoring (REAL — Day 45)
    # ========================================
    
    print(f"[{timestamp}] ⚠️  Calculating risk score...")
    
    # Include all text sources for risk assessment
    risk_text = incident["description"]
    if transcript and not transcript.startswith("[Transcription failed"):
        risk_text += " " + transcript
    if image_caption and not image_caption.startswith("["):
        risk_text += " " + image_caption
    
    try:
        risk_result = await calculate_risk_score(risk_text)
        risk_score = risk_result["score"]
        print(f"[{timestamp}] ✅ Risk score: {risk_score:.4f} (via {risk_result['method']})")
    except Exception as e:
        print(f"[{timestamp}] ❌ Risk scoring error: {str(e)}")
        severity_defaults = {"high": 0.8, "medium": 0.5, "low": 0.2}
        risk_score = severity_defaults.get(severity, 0.5)
    
    
    # ========================================
    # STEP 7: Update Database with All AI Results
    # ========================================
    
    print(f"[{timestamp}] 💾 Saving AI results to database...")
    
    # Build UPDATE query with ALL AI-generated fields
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,           # REAL from Whisper ASR (Day 34)
            image_caption=image_caption,    # REAL from BLIP (Day 48) NEW
            incident_type=incident_type,    # REAL from BART-MNLI (Day 46)
            severity=severity,              # REAL from BART-MNLI (Day 46)
            summary=summary,                # REAL from BART-Large-CNN (Day 47)
            risk_score=risk_score,          # REAL from BART-MNLI (Day 45)
        )
    )
    
    await database.execute(update_query)
    
    print(f"[{timestamp}] ✅ Processing complete for incident {incident_id}")
    print(f"[{timestamp}] {'=' * 60}")


# ========================================
# IMPLEMENTATION STATUS (Day 48) — FULLY MULTIMODAL
# ========================================

# ✅ REAL: Audio transcription (Day 34) - openai/whisper-base
# ✅ REAL: Image analysis (Day 48) - Salesforce/blip-image-captioning-base
# ✅ REAL: Text classification (Day 46) - facebook/bart-large-mnli
# ✅ REAL: Summarization (Day 47) - facebook/bart-large-cnn
# ✅ REAL: Risk scoring (Day 45) - facebook/bart-large-mnli
#
# Four models, three modalities (audio + text + images), zero stubs!