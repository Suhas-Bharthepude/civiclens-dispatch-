# backend/scripts/test_classifier.py
# Test script for the text classification service
# Run this BEFORE integrating into the pipeline to verify the model works
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   python scripts/test_classifier.py
#
# What this does:
#   1. Sends several sample incident texts to the classifier
#   2. Prints the predicted incident type and severity for each
#   3. Checks if predictions match expected values
#
# Day 46: Text classification service testing

# Import asyncio to run async functions from synchronous code
import asyncio

# Import sys and os to fix Python import paths
import sys
import os

# Add the backend directory to Python's path
# This lets us import from app/ when running from scripts/ folder
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our text classification function
from app.services.text_classifier import classify_incident


# ========================================
# TEST CASES
# ========================================

# Each test case is: (text, expected_type, expected_severity)
# These cover all 7 incident types and all 3 severity levels
TEST_CASES = [
    (
        # Test 1: Fire — should classify as fire, high severity
        "Building on fire, people are trapped on the third floor. "
        "Smoke is filling the stairwell and explosions heard from basement.",
        "fire",
        "high"
    ),
    (
        # Test 2: Medical — should classify as medical, high severity
        "Person collapsed on the sidewalk, not breathing. "
        "Bystander performing CPR. Need ambulance immediately.",
        "medical",
        "high"
    ),
    (
        # Test 3: Traffic — should classify as traffic, medium or high severity
        "Two-car collision at the intersection of Oak and Main. "
        "One vehicle flipped on its side. Driver appears conscious but injured.",
        "traffic",
        "medium"  # Could also be "high" — both are acceptable
    ),
    (
        # Test 4: Crime — should classify as crime, high severity
        "Armed robbery in progress at the convenience store on 5th Avenue. "
        "Two masked suspects, one appears to have a weapon. Customers inside.",
        "crime",
        "high"
    ),
    (
        # Test 5: Noise — should classify as noise, low severity
        "Neighbor at 456 Oak Avenue playing extremely loud music at 2am. "
        "This is the third time this week. Other residents are complaining.",
        "noise",
        "low"
    ),
    (
        # Test 6: Infrastructure — should classify as infrastructure, medium severity
        "Large pothole opened up on Elm Street near the school. "
        "Water main appears to be leaking underneath. Road is partially flooded.",
        "infrastructure",
        "medium"
    ),
    (
        # Test 7: Other/edge case — ambiguous text
        "Strange smell coming from the abandoned building on Park Road. "
        "Not sure what it is but several people in the area are concerned.",
        "other",  # Could be various types — model may pick something else
        "medium"
    ),
    (
        # Test 8: Low severity fire — small fire, already handled
        "Small grease fire in kitchen, already extinguished with fire blanket. "
        "No injuries, no structural damage. Just reporting for the record.",
        "fire",
        "low"  # The model should recognize this is low severity despite being fire
    ),
]


# ========================================
# MAIN TEST FUNCTION
# ========================================

async def run_tests():
    """
    Run all test cases and display results.
    """
    
    # Print header
    print("=" * 70)
    print("🏷️  TEXT CLASSIFICATION SERVICE TEST")
    print("=" * 70)
    print()
    print(f"Testing with {len(TEST_CASES)} sample incidents...")
    print("Model: facebook/bart-large-mnli (zero-shot classification)")
    print("Two passes per incident: type + severity")
    print("First request may take 20-30 seconds (model loading)...")
    print()
    
    # Track results
    type_correct = 0
    severity_correct = 0
    total = len(TEST_CASES)
    
    # Run each test
    for i, (text, expected_type, expected_severity) in enumerate(TEST_CASES, 1):
        
        # Print test header
        print(f"--- Test {i}/{total} ---")
        print(f"  Text: \"{text[:80]}...\"")
        print(f"  Expected: type={expected_type}, severity={expected_severity}")
        print(f"  Classifying...")
        
        # Call the classifier
        result = await classify_incident(text)
        
        # Extract results
        predicted_type = result["incident_type"]
        predicted_severity = result["severity"]
        type_conf = result["type_confidence"]
        severity_conf = result["severity_confidence"]
        method = result["method"]
        
        # Print results
        print(f"  Result: type={predicted_type} ({type_conf:.2f}), severity={predicted_severity} ({severity_conf:.2f}) [method: {method}]")
        
        # Check type match
        if predicted_type == expected_type:
            print(f"  ✅ Type correct: {predicted_type}")
            type_correct += 1
        else:
            print(f"  ⚠️  Type mismatch: got {predicted_type}, expected {expected_type}")
            print(f"     (This is OK — ML models interpret context differently)")
        
        # Check severity match
        if predicted_severity == expected_severity:
            print(f"  ✅ Severity correct: {predicted_severity}")
            severity_correct += 1
        else:
            print(f"  ⚠️  Severity mismatch: got {predicted_severity}, expected {expected_severity}")
            print(f"     (This is OK — severity is subjective)")
        
        print()
    
    # Print summary
    print("=" * 70)
    print(f"RESULTS:")
    print(f"  Type accuracy:     {type_correct}/{total} ({type_correct/total*100:.0f}%)")
    print(f"  Severity accuracy: {severity_correct}/{total} ({severity_correct/total*100:.0f}%)")
    print("=" * 70)
    
    # Assessment
    combined = type_correct + severity_correct
    combined_total = total * 2
    
    if combined >= combined_total * 0.7:
        print("✅ Classifier is working well!")
    elif combined >= combined_total * 0.5:
        print("⚠️  Classifier is working but has some disagreements.")
        print("   This is normal for zero-shot — the model interprets context.")
    else:
        print("❌ Classifier may have issues. Check API key and model availability.")
    
    print()
    print("Note: Zero-shot classification is approximate.")
    print("Edge cases and ambiguous texts may be classified differently than expected.")
    print("What matters is that clear-cut cases (fire, medical, noise) are classified correctly.")


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_tests())