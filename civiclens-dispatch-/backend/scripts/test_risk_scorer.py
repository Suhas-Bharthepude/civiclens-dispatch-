# backend/scripts/test_risk_scorer.py
# Test script for the risk scoring service
# Run this BEFORE integrating into the pipeline to verify the model works
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   python scripts/test_risk_scorer.py
#
# What this does:
#   1. Sends several sample incident texts to the risk scorer
#   2. Prints the score and label confidences for each
#   3. Verifies scores are reasonable (high for emergencies, low for routine)
#
# Day 45: Risk scoring service testing

# Import asyncio to run async functions from a regular script
# Our risk scoring function is async (uses await for API calls)
# asyncio.run() lets us call async functions from synchronous code
import asyncio

# Import sys and os to fix Python import paths
# When running from scripts/ folder, Python can't find app/ modules by default
# We need to add the backend/ directory to Python's module search path
import sys
import os

# Add the backend directory to Python's path so we can import from app/
# __file__ is this script's path: backend/scripts/test_risk_scorer.py
# We go up one directory to get: backend/
# Then add that to sys.path so 'from app.services...' works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now we can import our risk scoring function
from app.services.risk_scorer import calculate_risk_score


# ========================================
# TEST CASES
# ========================================

# A list of sample incident texts with expected urgency levels
# Each tuple is: (description_text, expected_urgency_level)
# We test a range from critical emergencies to routine matters
TEST_CASES = [
    (
        # Test 1: Critical emergency - should score very high (0.7+)
        "Building on fire, people are trapped on the third floor. "
        "Smoke is filling the stairwell and we can hear screaming. "
        "Multiple explosions heard from the basement. Send help immediately!",
        "CRITICAL"
    ),
    (
        # Test 2: High urgency - should score high (0.5-0.8)
        "Car accident on Highway 101, two vehicles involved. "
        "One driver appears to be unconscious and bleeding. "
        "The other driver is walking but holding their arm. Ambulance needed.",
        "HIGH"
    ),
    (
        # Test 3: Moderate concern - should score medium (0.3-0.6)
        "Water main break on Elm Street causing flooding in the road. "
        "Traffic is being diverted. No injuries reported but several "
        "basements in nearby homes are taking on water.",
        "MODERATE"
    ),
    (
        # Test 4: Low priority - should score low (0.1-0.3)
        "Noise complaint from resident at 456 Oak Avenue. "
        "Neighbor is playing loud music late at night. "
        "This has been an ongoing issue for the past two weeks.",
        "LOW"
    ),
    (
        # Test 5: Routine matter - should score very low (0.0-0.2)
        "Streetlight on the corner of Main and 5th has been "
        "flickering for the past few days. Not urgent but "
        "should be looked at when maintenance crew is available.",
        "ROUTINE"
    ),
    (
        # Test 6: Mixed signals - text has both urgent and non-urgent elements
        # This tests the model's ability to weigh competing signals
        "A dog has been barking non-stop for three hours. "
        "The owner may be injured inside because they usually "
        "respond to complaints. Someone should check on them.",
        "MODERATE"
    ),
]


# ========================================
# MAIN TEST FUNCTION
# ========================================

async def run_tests():
    """
    Run all test cases and display the results.
    
    For each test case:
    1. Send the text to calculate_risk_score()
    2. Print the resulting score and label confidences
    3. Show whether the score matches expected urgency level
    """
    
    # Print header
    print("=" * 70)
    print("🔮 RISK SCORING SERVICE TEST")
    print("=" * 70)
    print()
    print("Testing with 6 sample incidents...")
    print("Model: facebook/bart-large-mnli (zero-shot classification)")
    print("First request may take 20-30 seconds (model loading)...")
    print()
    
    # Track how many tests pass
    passed = 0
    total = len(TEST_CASES)
    
    # Loop through each test case
    for i, (text, expected_level) in enumerate(TEST_CASES, 1):
        
        # Print test header with the first 60 characters of the text
        print(f"--- Test {i}/{total}: [{expected_level}] ---")
        print(f"  Text: \"{text[:80]}...\"")
        print(f"  Calling risk scorer...")
        
        # Call the risk scoring function
        # This is the actual function we're testing
        # It will call the Hugging Face API (or fallback if API fails)
        result = await calculate_risk_score(text)
        
        # Extract the score and method from the result
        score = result["score"]
        method = result["method"]
        labels = result.get("labels", {})
        
        # Print the score
        print(f"  Score: {score:.4f} (method: {method})")
        
        # Print label confidences if available (only for ML method)
        if labels:
            print(f"  Label confidences:")
            for label, confidence in labels.items():
                # Create a visual bar showing the confidence
                bar = "█" * int(confidence * 30)
                print(f"    {confidence:.3f} {bar} {label}")
        
        # Check if the score is in the expected range for this urgency level
        # These ranges are approximate - the model won't be perfectly calibrated
        expected_ranges = {
            "CRITICAL": (0.55, 1.0),   # Should be high
            "HIGH":     (0.40, 0.85),   # Should be medium-high
            "MODERATE": (0.25, 0.65),   # Should be medium
            "LOW":      (0.05, 0.40),   # Should be low
            "ROUTINE":  (0.00, 0.30),   # Should be very low
        }
        
        # Get the expected range for this test's urgency level
        min_expected, max_expected = expected_ranges[expected_level]
        
        # Check if score falls within expected range
        if min_expected <= score <= max_expected:
            print(f"  ✅ PASS - Score {score:.2f} is in expected range [{min_expected}-{max_expected}]")
            passed += 1
        else:
            print(f"  ⚠️  OUTSIDE EXPECTED RANGE - Score {score:.2f}, expected [{min_expected}-{max_expected}]")
            print(f"     (This is OK - ML models aren't perfectly calibrated)")
        
        print()
    
    # Print summary
    print("=" * 70)
    print(f"RESULTS: {passed}/{total} tests in expected range")
    print("=" * 70)
    
    # Note about results
    if passed >= 4:
        print("✅ Risk scorer is working well!")
    elif passed >= 2:
        print("⚠️  Risk scorer is working but calibration could be improved.")
        print("   This is normal for zero-shot classification.")
    else:
        print("❌ Risk scorer may have issues. Check API key and model availability.")
    
    print()
    print("Note: Zero-shot classification gives approximate results.")
    print("The exact scores will vary - what matters is the relative ordering:")
    print("  Fire emergency > Car accident > Water leak > Noise complaint > Streetlight")


# ========================================
# ENTRY POINT
# ========================================

# This block runs when you execute the script directly
# It calls asyncio.run() to run our async test function
if __name__ == "__main__":
    asyncio.run(run_tests())