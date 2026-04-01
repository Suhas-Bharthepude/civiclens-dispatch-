# backend/scripts/test_pipeline_timing.py
# Test script that creates a test incident and runs it through
# the optimized pipeline, showing timing for each phase.
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   PYTHONPATH=. python scripts/test_pipeline_timing.py
#
# What this does:
#   1. Creates a test incident in the database
#   2. Runs the full AI pipeline on it
#   3. Prints timing breakdown (Phase 1 vs Phase 2)
#   4. Shows the final AI-generated results
#
# Day 49: Pipeline optimization testing

# Import asyncio to run async functions
import asyncio

# Import time for measuring total elapsed time
import time

# Import sys and os for path fixing
import sys
import os

# Add the backend directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database components
from app.db.database import database, engine
from app.db.models import incidents, metadata

# Import the optimized pipeline
from app.services.incident_processor import process_incident


# ========================================
# TEST FUNCTION
# ========================================

async def run_pipeline_test():
    """
    Create a test incident and run the full optimized pipeline on it.
    """
    
    print("=" * 70)
    print("⚡ PIPELINE TIMING TEST")
    print("=" * 70)
    print()
    print("This test creates a sample incident and runs the full AI pipeline.")
    print("Watch for parallel processing — Phase 1 and Phase 2 should run")
    print("their sub-tasks simultaneously.")
    print()
    
    # Ensure database tables exist
    metadata.create_all(engine)
    
    # Connect to the database
    await database.connect()
    
    try:
        # Create a test incident with a detailed description
        # This gives the AI services enough text to work with
        test_description = (
            "Major vehicle collision reported on Highway 101 near exit 42. "
            "Two cars and a truck involved. At least one person appears to be "
            "trapped in the overturned vehicle. Witnesses report seeing smoke "
            "coming from the engine of one car. Traffic is backed up for miles. "
            "Several bystanders are attempting to help the trapped driver. "
            "The road surface is wet from recent rain which may have contributed "
            "to the accident. Emergency services have been called."
        )
        
        # Insert the test incident into the database
        query = incidents.insert().values(
            source="pipeline_test",
            description=test_description,
            location="Highway 101, Exit 42",
        )
        
        # Execute the insert and get the new incident's ID
        incident_id = await database.execute(query)
        
        print(f"✅ Created test incident #{incident_id}")
        print(f"   Description: \"{test_description[:80]}...\"")
        print(f"   Location: Highway 101, Exit 42")
        print(f"   Audio: None (text-only test)")
        print(f"   Image: None (text-only test)")
        print()
        
        # Record the total start time
        total_start = time.perf_counter()
        
        # Run the full pipeline on this incident
        print("🚀 Running optimized pipeline...")
        print()
        
        await process_incident(incident_id, "Pipeline timing test")
        
        # Record total elapsed time
        total_elapsed = time.perf_counter() - total_start
        
        # Fetch the processed incident to show results
        query = incidents.select().where(incidents.c.id == incident_id)
        result = await database.fetch_one(query)
        
        # Print the AI-generated results
        print()
        print("=" * 70)
        print("📊 AI RESULTS:")
        print("=" * 70)
        print(f"  Type:      {result['incident_type']}")
        print(f"  Severity:  {result['severity']}")
        print(f"  Risk:      {result['risk_score']}")
        print(f"  Summary:   {result['summary'][:100] if result['summary'] else 'None'}...")
        print(f"  Transcript: {'Yes' if result['transcript'] else 'None (no audio)'}")
        print(f"  Image:     {'Yes' if result['image_caption'] else 'None (no image)'}")
        print()
        print(f"⏱️  TOTAL PIPELINE TIME: {total_elapsed:.1f} seconds")
        print()
        
        # Performance assessment
        if total_elapsed < 15:
            print("🏎️  Excellent! Pipeline completed in under 15 seconds.")
        elif total_elapsed < 30:
            print("✅ Good. Pipeline completed in under 30 seconds.")
        elif total_elapsed < 60:
            print("⚠️  Moderate. Pipeline took 30-60 seconds (free tier latency).")
        else:
            print("🐢 Slow. Pipeline took over 60 seconds (likely model loading delays).")
        
        print()
        print("Note: First run is always slower (model cold starts).")
        print("Run this test again immediately — the second run will be faster")
        print("because the models are already loaded on Hugging Face's servers.")
        
        # Clean up the test incident
        await database.execute(
            incidents.delete().where(incidents.c.id == incident_id)
        )
        print(f"\n🧹 Cleaned up test incident #{incident_id}")
    
    finally:
        # Always disconnect from the database
        await database.disconnect()


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_pipeline_test())