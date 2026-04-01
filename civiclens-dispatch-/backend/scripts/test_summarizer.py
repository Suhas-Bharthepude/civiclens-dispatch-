# backend/scripts/test_summarizer.py
# Test script for the summarization service
# Run this BEFORE integrating into the pipeline to verify the model works
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   python scripts/test_summarizer.py
#
# What this does:
#   1. Sends several sample incident texts to the summarizer
#   2. Prints the generated summary for each
#   3. Shows input vs output length (compression ratio)
#
# Day 47: Summarization service testing

# Import asyncio to run async functions from synchronous code
import asyncio

# Import sys and os to fix Python import paths
import sys
import os

# Add the backend directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our summarization function
from app.services.summarizer import summarize_text


# ========================================
# TEST CASES
# ========================================

# Sample incident texts of varying length and complexity
# Each is: (description, label_for_display)
TEST_CASES = [
    (
        # Test 1: Detailed fire incident (long text — good for summarization)
        "A major fire has broken out at the Riverside Shopping Center on Oak Boulevard. "
        "The fire appears to have started in a kitchen area of one of the restaurants "
        "on the second floor and has rapidly spread to adjacent stores. Multiple fire "
        "trucks have arrived on scene. At least 200 customers and staff have been "
        "evacuated from the building. Three people have been reported injured, with "
        "two suffering from smoke inhalation and one with minor burns. The parking "
        "lot is being used as a staging area. Black smoke is visible from several "
        "miles away. Traffic on Oak Boulevard has been diverted in both directions. "
        "The fire chief has called for additional units from neighboring districts.",
        "FIRE - Detailed report"
    ),
    (
        # Test 2: Car accident with transcript context
        "Two-vehicle collision on Highway 101 southbound near exit 42. A sedan rear-ended "
        "a pickup truck causing the pickup to roll over. The sedan driver is unconscious "
        "and trapped in the vehicle. The pickup driver was ejected and is lying on the "
        "road shoulder. Both vehicles are blocking two lanes of traffic. A fuel leak has "
        "been detected from the sedan. Emergency medical services have been dispatched. "
        "Multiple bystanders are at the scene attempting to help. Highway patrol is "
        "requesting traffic diversion through exit 41.",
        "TRAFFIC - Highway accident"
    ),
    (
        # Test 3: Short text (should use passthrough — too short to summarize)
        "Noise complaint from apartment 4B. Loud music at 2am.",
        "NOISE - Short text (should passthrough)"
    ),
    (
        # Test 4: Medium-length infrastructure report
        "Water main break reported on Elm Street between 3rd and 4th Avenue. Water is "
        "flooding the intersection and flowing into several basement units of nearby "
        "apartment buildings. Public works has been notified and a crew is en route. "
        "Residents are advised to avoid the area. Estimated repair time is 4 to 6 hours. "
        "Approximately 50 households may experience water service disruption.",
        "INFRASTRUCTURE - Water main"
    ),
    (
        # Test 5: Incident with description + transcript combined
        "Armed robbery reported at First National Bank on Main Street. "
        "Two suspects entered the bank wearing masks. Security guard was "
        "assaulted. Suspects fled in a dark SUV heading eastbound. "
        "Caller transcript: I was in the bank when two men came in with guns. "
        "They forced everyone to the ground and made the tellers open the vault. "
        "The security guard tried to stop them and they hit him with the gun. "
        "Then they ran out and got into a dark colored SUV. It happened so fast. "
        "There were maybe ten customers in the bank at the time. Everyone is scared.",
        "CRIME - Bank robbery with transcript"
    ),
]


# ========================================
# MAIN TEST FUNCTION
# ========================================

async def run_tests():
    """
    Run all test cases and display the generated summaries.
    """
    
    # Print header
    print("=" * 70)
    print("📝 SUMMARIZATION SERVICE TEST")
    print("=" * 70)
    print()
    print(f"Testing with {len(TEST_CASES)} sample incidents...")
    print("Model: facebook/bart-large-cnn (abstractive summarization)")
    print("First request may take 30-60 seconds (model loading)...")
    print()
    
    # Run each test
    for i, (text, label) in enumerate(TEST_CASES, 1):
        
        # Print test header
        print(f"--- Test {i}/{len(TEST_CASES)}: {label} ---")
        print(f"  Input ({len(text)} chars): \"{text[:100]}...\"")
        print(f"  Summarizing...")
        
        # Call the summarizer
        result = await summarize_text(text)
        
        # Extract results
        summary = result["summary"]
        method = result["method"]
        in_len = result["input_length"]
        out_len = result["output_length"]
        
        # Calculate compression ratio
        # How much shorter is the summary compared to the input?
        if in_len > 0:
            compression = (1 - out_len / in_len) * 100
        else:
            compression = 0
        
        # Print results
        print(f"  Method: {method}")
        print(f"  Summary ({out_len} chars): \"{summary}\"")
        print(f"  Compression: {compression:.0f}% reduction ({in_len} → {out_len} chars)")
        
        # Quality check
        if method == "ml":
            if out_len < in_len:
                print(f"  ✅ Summary is shorter than input (good!)")
            else:
                print(f"  ⚠️  Summary is longer than input (unusual for summarization)")
        elif method == "passthrough":
            print(f"  ℹ️  Text was too short to summarize — returned as-is")
        elif method == "fallback":
            print(f"  ⚠️  Used fallback (API was unavailable)")
        
        print()
    
    # Print summary
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("What to check:")
    print("  1. ML summaries should be shorter than input text")
    print("  2. Summaries should capture the key facts (what, where, who)")
    print("  3. Short texts should passthrough (not be summarized)")
    print("  4. Summaries should be grammatically correct")
    print()
    print("If most summaries look reasonable, the service is working!")


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_tests())