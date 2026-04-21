# backend/app/services/incident_processor.py
# Incident processing pipeline - orchestrates all AI services
# Runs in background after incident is created or updated
#
# Day 49: OPTIMIZED with parallel processing and timing!
#
# Pipeline structure:
#   Phase 1 (parallel): ASR transcription + Image analysis
#   Phase 2 (parallel): Classification + Summarization + Risk scoring
#   These phases run their tasks simultaneously using asyncio.gather()
#
# Why two phases?
#   Phase 2 needs the transcript from Phase 1 (can't start until ASR is done)
#   But within each phase, tasks are independent and run at the same time
#
# Models used:
#   - openai/whisper-base (ASR)
#   - facebook/detr-resnet-50 (image analysis)
#   - facebook/bart-large-mnli (classification + risk scoring)
#   - facebook/bart-large-cnn (summarization)

# Import asyncio for parallel processing with gather() and timing
import asyncio

# Import time for measuring how long each step takes
# time.perf_counter() gives high-precision timestamps for benchmarking
import time

# Import datetime for human-readable log timestamps
from datetime import datetime

# Import database connection for fetching and updating incidents
from app.db.database import database

# Import incidents table definition for building SQL queries
from app.db.models import incidents

# Import all AI services
from app.services.asr import transcribe_audio
from app.services.image_analyzer import analyze_image
from app.services.text_classifier import classify_incident
from app.services.summarizer import summarize_text
from app.services.risk_scorer import calculate_risk_score


# ========================================
# HELPER: TIMED TASK WRAPPER
# ========================================

async def _timed_task(name: str, coro):
    """
    Run an async task and measure how long it takes.
    
    This wraps any async function call with a timer so we can see
    exactly how many seconds each AI service takes to complete.
    
    Args:
        name: Human-readable name for the task (for logging)
        coro: The coroutine (async function call) to run and time
    
    Returns:
        tuple of (result, elapsed_seconds)
        If the task fails, result will be an Exception object
    """
    
    # Record the start time using perf_counter (most precise timer available)
    start = time.perf_counter()
    
    try:
        # Await the actual async task (e.g., transcribe_audio, analyze_image)
        result = await coro
        
        # Calculate how long it took
        elapsed = time.perf_counter() - start
        
        # Log the timing
        print(f"    ⏱️  {name}: {elapsed:.1f}s")
        
        # Return both the result and the elapsed time
        return result, elapsed
    
    except Exception as e:
        # If the task failed, still record the timing
        elapsed = time.perf_counter() - start
        print(f"    ⏱️  {name}: {elapsed:.1f}s (FAILED: {str(e)[:80]})")
        
        # Return the exception as the result (not raising it)
        # This lets the pipeline continue even if one task fails
        return e, elapsed


# ========================================
# MAIN PROCESSING FUNCTION
# ========================================

async def process_incident(incident_id: int, log_message: str = None) -> None:
    """
    AI processing pipeline for a single incident.
    
    OPTIMIZED with parallel processing (Day 49):
    
    Phase 1 (parallel):
        - ASR transcription (if audio exists)
        - Image analysis (if image exists)
    
    Phase 2 (parallel — needs Phase 1 results):
        - Text classification → incident_type, severity
        - Summarization → summary
        - Risk scoring → risk_score
    
    All steps are timed and logged for performance monitoring.
    If any individual task fails, the others still complete.
    """
    
    # Record the start time of the entire pipeline
    pipeline_start = time.perf_counter()
    
    # Get current timestamp for log messages
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Log the start of processing
    print(f"\n[{timestamp}] {'=' * 60}")
    print(f"[{timestamp}] 🤖 Processing incident {incident_id} (OPTIMIZED)")
    
    if log_message:
        print(f"[{timestamp}] 📋 {log_message}")
    
    
    # ========================================
    # STEP 1: Fetch Incident from Database
    # ========================================
    
    step1_start = time.perf_counter()
    print(f"[{timestamp}] 📥 Fetching incident {incident_id} from database...")
    
    # Build and execute SELECT query
    query = incidents.select().where(incidents.c.id == incident_id)
    incident = await database.fetch_one(query)
    
    # Check if incident exists
    if not incident:
        print(f"[{timestamp}] ❌ Incident {incident_id} not found in database")
        return
    
    step1_time = time.perf_counter() - step1_start
    print(f"[{timestamp}] 📥 Fetched: {incident['description'][:60]}...")
    print(f"    ⏱️  DB fetch: {step1_time:.1f}s")
    
    
    # ========================================
    # PHASE 1: Media Processing (PARALLEL)
    # ASR + Image Analysis run at the same time
    # ========================================
    
    print(f"\n[{timestamp}] 🔀 PHASE 1: Media processing (parallel)...")
    phase1_start = time.perf_counter()
    
    # Build the list of Phase 1 tasks to run in parallel
    # We only add tasks that have something to process
    phase1_tasks = []
    phase1_names = []
    
    # Check if audio exists — add ASR task
    has_audio = bool(incident["audio_path"])
    if has_audio:
        print(f"[{timestamp}]   🎤 Audio found: {incident['audio_path']}")
        phase1_tasks.append(
            _timed_task("ASR transcription", transcribe_audio(incident["audio_path"]))
        )
        phase1_names.append("asr")
    else:
        print(f"[{timestamp}]   ℹ️  No audio file — skipping ASR")
    
    # Check if image exists — add image analysis task
    has_image = bool(incident["image_path"])
    if has_image:
        print(f"[{timestamp}]   🖼️  Image found: {incident['image_path']}")
        phase1_tasks.append(
            _timed_task("Image analysis", analyze_image(incident["image_path"]))
        )
        phase1_names.append("image")
    else:
        print(f"[{timestamp}]   ℹ️  No image file — skipping image analysis")
    
    # Run Phase 1 tasks in parallel using asyncio.gather()
    # asyncio.gather() starts all tasks at the same time and waits for ALL to finish
    # The total time is the time of the SLOWEST task, not the sum of all tasks
    transcript = None
    image_caption = None
    
    if phase1_tasks:
        # gather() returns results in the same order as the input tasks
        phase1_results = await asyncio.gather(*phase1_tasks)
        
        # Extract results based on which tasks we added
        result_index = 0
        
        if has_audio:
            # Get ASR result — it's a tuple of (result, elapsed_time)
            asr_result, asr_time = phase1_results[result_index]
            result_index += 1
            
            # Check if ASR succeeded or failed
            if isinstance(asr_result, Exception):
                # ASR failed — store error message but continue
                print(f"[{timestamp}]   ⚠️  ASR failed: {str(asr_result)[:80]}")
                transcript = f"[Transcription failed: {str(asr_result)}]"
            else:
                # ASR succeeded — store the transcript
                transcript = asr_result
                print(f"[{timestamp}]   ✅ Transcript: {transcript[:80]}...")
        
        if has_image:
            # Get image analysis result
            image_result, image_time = phase1_results[result_index]
            result_index += 1
            
            # Check if image analysis succeeded or failed
            if isinstance(image_result, Exception):
                print(f"[{timestamp}]   ⚠️  Image analysis failed: {str(image_result)[:80]}")
                image_caption = f"[Image analysis failed: {str(image_result)}]"
            elif isinstance(image_result, dict):
                # image_result is a dict with 'caption', 'method', etc.
                image_caption = image_result.get("caption", "[No caption]")
                print(f"[{timestamp}]   ✅ Image: {image_caption[:80]}")
            else:
                image_caption = str(image_result)
    
    phase1_time = time.perf_counter() - phase1_start
    print(f"[{timestamp}]   ⏱️  Phase 1 total: {phase1_time:.1f}s")
    
    
    # ========================================
    # PHASE 2: Text Analysis (PARALLEL)
    # Classification + Summarization + Risk Scoring run at the same time
    # These all need the text from Phase 1, so they run AFTER Phase 1
    # ========================================
    
    print(f"\n[{timestamp}] 🔀 PHASE 2: Text analysis (parallel)...")
    phase2_start = time.perf_counter()
    
    # Build the combined text that all Phase 2 services will analyze
    # Start with the description (always available)
    combined_text = incident["description"]
    
    # Add transcript if available and valid
    if transcript and not transcript.startswith("[Transcription failed"):
        combined_text += " " + transcript
    
    # Add image caption if available and valid
    if image_caption and not image_caption.startswith("["):
        combined_text += " Image shows: " + image_caption
    
    # Build the text inputs for each service
    # Classification gets everything (description + transcript + image caption)
    classify_text = combined_text
    
    # Summarization gets everything
    summary_text = combined_text
    
    # Risk scoring gets everything
    risk_text = combined_text
    
    # Run all three Phase 2 tasks in parallel
    # These are independent — classification doesn't need to wait for summarization
    phase2_results = await asyncio.gather(
        _timed_task("Classification", classify_incident(classify_text)),
        _timed_task("Summarization", summarize_text(summary_text)),
        _timed_task("Risk scoring", calculate_risk_score(risk_text)),
    )
    
    # Extract classification result
    classify_result, classify_time = phase2_results[0]
    if isinstance(classify_result, Exception):
        print(f"[{timestamp}]   ⚠️  Classification failed: {str(classify_result)[:80]}")
        incident_type = "other"
        severity = "medium"
    else:
        incident_type = classify_result["incident_type"]
        severity = classify_result["severity"]
        method = classify_result["method"]
        print(f"[{timestamp}]   ✅ Type: {incident_type} ({severity}) [via {method}]")
    
    # Extract summarization result
    summary_result, summary_time = phase2_results[1]
    if isinstance(summary_result, Exception):
        print(f"[{timestamp}]   ⚠️  Summarization failed: {str(summary_result)[:80]}")
        # Fallback: truncate description
        summary = incident["description"][:150] + "..." if len(incident["description"]) > 150 else incident["description"]
    else:
        summary = summary_result["summary"]
        method = summary_result["method"]
        print(f"[{timestamp}]   ✅ Summary (via {method}): {summary[:80]}...")
    
    # Extract risk scoring result
    risk_result, risk_time = phase2_results[2]
    if isinstance(risk_result, Exception):
        print(f"[{timestamp}]   ⚠️  Risk scoring failed: {str(risk_result)[:80]}")
        severity_defaults = {"high": 0.8, "medium": 0.5, "low": 0.2}
        risk_score = severity_defaults.get(severity, 0.5)
    else:
        risk_score = risk_result["score"]
        method = risk_result["method"]
        print(f"[{timestamp}]   ✅ Risk: {risk_score:.4f} [via {method}]")
    
    phase2_time = time.perf_counter() - phase2_start
    print(f"[{timestamp}]   ⏱️  Phase 2 total: {phase2_time:.1f}s")

    # Calibrate risk score so it reflects the determined severity.
    # The ML weighted-sum produces mid-range values (~0.5-0.65) even for
    # clearly critical incidents, so we enforce minimum/maximum bounds here.
    if severity == "high":
        risk_score = max(risk_score, 0.75)
    elif severity == "low":
        risk_score = min(risk_score, 0.30)
    risk_score = round(risk_score, 4)
    print(f"[{timestamp}]   📊 Final risk (after severity calibration): {risk_score:.4f} [{severity}]")


    # ========================================
    # STEP 3: Save All Results to Database
    # ========================================
    
    print(f"\n[{timestamp}] 💾 Saving AI results to database...")
    save_start = time.perf_counter()
    
    # Build UPDATE query with ALL AI-generated fields
    update_query = (
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript=transcript,
            image_caption=image_caption,
            incident_type=incident_type,
            severity=severity,
            summary=summary,
            risk_score=risk_score,
        )
    )
    
    # Execute the update
    await database.execute(update_query)
    
    save_time = time.perf_counter() - save_start
    print(f"    ⏱️  DB save: {save_time:.1f}s")
    
    
    # ── WEBSOCKET BROADCAST (Day 71) ──────────────────────────
    # After all AI fields are saved, push the updated incident to every
    # connected dashboard.  This lets the UI replace the stale row
    # without a poll.  Wrapped in try/except so a WebSocket failure
    # never kills the pipeline or raises an unhandled exception.
    try:
        from app.websocket_manager import manager as ws_manager
        # Re-fetch the row so the broadcast includes all AI fields we just saved
        updated = await database.fetch_one(
            incidents.select().where(incidents.c.id == incident_id)
        )
        if updated:
            await ws_manager.broadcast({
                "event": "incident_updated",
                "incident": dict(updated),
            })
    except Exception as ws_err:
        # Log but do not raise — pipeline success must not depend on WS
        print(f"[{timestamp}]   ⚠️  WebSocket broadcast failed: {str(ws_err)[:80]}")


    # ========================================
    # PIPELINE COMPLETE — Print Timing Summary
    # ========================================

    pipeline_total = time.perf_counter() - pipeline_start
    
    print(f"\n[{timestamp}] {'=' * 60}")
    print(f"[{timestamp}] ✅ PROCESSING COMPLETE for incident {incident_id}")
    print(f"[{timestamp}] ⏱️  TIMING SUMMARY:")
    print(f"[{timestamp}]     DB fetch:  {step1_time:.1f}s")
    print(f"[{timestamp}]     Phase 1:   {phase1_time:.1f}s (ASR + Image — parallel)")
    print(f"[{timestamp}]     Phase 2:   {phase2_time:.1f}s (Classify + Summarize + Risk — parallel)")
    print(f"[{timestamp}]     DB save:   {save_time:.1f}s")
    print(f"[{timestamp}]     ─────────────────")
    print(f"[{timestamp}]     TOTAL:     {pipeline_total:.1f}s")
    print(f"[{timestamp}] {'=' * 60}")


# ========================================
# IMPLEMENTATION STATUS (Day 49) — OPTIMIZED
# ========================================

# ✅ Parallel Phase 1: ASR + Image analysis (simultaneous)
# ✅ Parallel Phase 2: Classification + Summarization + Risk scoring (simultaneous)
# ✅ Per-step timing measurements
# ✅ Total pipeline duration tracking
# ✅ Graceful error handling (one failure doesn't kill others)
#
# Models:
#   - openai/whisper-base (ASR)
#   - facebook/detr-resnet-50 (image detection)
#   - facebook/bart-large-mnli (classification + risk)
#   - facebook/bart-large-cnn (summarization)