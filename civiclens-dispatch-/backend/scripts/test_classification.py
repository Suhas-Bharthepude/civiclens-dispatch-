# backend/scripts/test_classification.py
#
# Test script for the classification service.
# Includes cases specifically designed to FAIL keyword matching
# but SUCCEED with zero-shot AI classification.
#
# Usage:
#   cd ~/Desktop/CivicLensDispatch/civiclens-dispatch-/backend
#   source ../.venv/bin/activate
#   python -m scripts.test_classification

# asyncio to run async functions from a regular script
import asyncio

# sys and os to fix the Python import path
import sys
import os

# Add the backend directory to Python's module search path
# Without this, "from app.services.classification import ..." would fail
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions we're testing
from app.services.classification import classify_incident, classify_by_keywords


# ============================================================
# TEST CASES
# ============================================================
# Each case has:
#   description:    The incident text
#   expected_type:  What we expect the classifier to return
#   keyword_fails:  True if the keyword stub would get this WRONG
#                   (proves the AI is doing real work)

TEST_CASES = [
    # ── Cases where keywords WORK (sanity check) ─────────
    {
        "name": "Obvious fire (keyword would work)",
        "description": "There is a fire at the apartment building on Oak Street.",
        "transcript": None,
        "expected_type": "fire",
        "keyword_fails": False,
    },
    {
        "name": "Obvious medical (keyword would work)",
        "description": "Someone is injured and needs an ambulance immediately.",
        "transcript": None,
        "expected_type": "medical",
        "keyword_fails": False,
    },

    # ── Cases where keywords FAIL (tests real AI) ─────────
    {
        "name": "Fire without 'fire' keyword",
        "description": "The structure is completely engulfed and residents are fleeing the building.",
        "transcript": None,
        "expected_type": "fire",
        "keyword_fails": True,  # No "fire", "smoke", "flames" keyword
    },
    {
        "name": "Medical without medical keywords",
        "description": "An elderly man collapsed on the sidewalk and is not responding to anyone.",
        "transcript": None,
        "expected_type": "medical",
        "keyword_fails": True,  # No "medical", "injured", "ambulance" keyword
    },
    {
        "name": "Crime without crime keywords",
        "description": "I came home to find someone had forced their way into my house.",
        "transcript": None,
        "expected_type": "crime",
        "keyword_fails": True,  # No "break", "robbery", "theft" keyword
    },
    {
        "name": "Traffic without traffic keywords",
        "description": "Two cars have collided at the intersection and one driver appears to be in pain.",
        "transcript": None,
        "expected_type": "traffic",
        "keyword_fails": False,  # "collided" might match "collision"
    },
    {
        "name": "Shots fired (escalated crime)",
        "description": "I heard multiple gunshots near the park entrance. People are running.",
        "transcript": None,
        "expected_type": "crime",
        "keyword_fails": True,  # "shots" not in keyword list (only "robbery", "theft")
    },
    {
        "name": "Infrastructure without keywords",
        "description": "There is a massive hole in the road that has damaged several vehicles.",
        "transcript": None,
        "expected_type": "infrastructure",
        "keyword_fails": True,  # No "pothole", "flood", "water main" keyword
    },

    # ── Case with transcript ──────────────────────────────
    {
        "name": "Medical with transcript (richer context)",
        "description": "Someone needs help at the downtown bus stop.",
        "transcript": (
            "There is an older woman who has fallen down and she is not moving. "
            "She appears to be unconscious. Her breathing seems very shallow. "
            "We need paramedics here right away."
        ),
        "expected_type": "medical",
        "keyword_fails": True,  # Description alone is too vague
    },
]


# ============================================================
# MAIN TEST FUNCTION
# ============================================================

async def run_tests():
    """
    Run all test cases and print results.
    """

    print()
    print("=" * 70)
    print("  CLASSIFICATION SERVICE TEST")
    print("  Testing: facebook/bart-large-mnli (zero-shot) via Hugging Face")
    print("=" * 70)
    print()

    passed = 0
    failed = 0
    ai_wins = 0  # Count cases where AI succeeds but keywords would fail

    for i, test in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test['name']}")

        if test["keyword_fails"]:
            print(f"  ⚠️  Keyword stub would FAIL this case — tests real AI")

        # Show description preview
        desc = test["description"]
        print(f"  Description: '{desc[:80]}{'...' if len(desc) > 80 else ''}'")

        if test["transcript"]:
            print(f"  Transcript: YES ({len(test['transcript'])} chars)")

        print(f"  Expected type: {test['expected_type']}")
        print()

        try:
            # Call the AI classification service
            print(f"  ⏳ Calling classify_incident()...")
            result = await classify_incident(
                description=test["description"],
                transcript=test["transcript"],
            )

            # Extract results
            got_type   = result["incident_type"]
            severity   = result["severity"]
            confidence = result["confidence"]
            method     = result["method"]

            # Check if the type matches expectation
            correct = got_type == test["expected_type"]

            if correct:
                print(f"  ✅ CORRECT: type={got_type}, severity={severity}, "
                      f"confidence={confidence:.0%}, method={method}")
                passed += 1
                if test["keyword_fails"]:
                    ai_wins += 1
                    print(f"  🏆 AI succeeded where keywords would have failed!")
            else:
                print(f"  ❌ WRONG: got type='{got_type}' (expected '{test['expected_type']}')")
                print(f"     severity={severity}, confidence={confidence:.0%}, method={method}")

                # Show all scores for debugging
                if result.get("top_scores"):
                    print(f"     All scores:")
                    # Sort by score descending for readability
                    sorted_scores = sorted(
                        result["top_scores"].items(),
                        key=lambda x: x[1],
                        reverse=True
                    )
                    for label, score in sorted_scores:
                        bar = "█" * int(score * 20)  # Visual bar
                        print(f"       {label:<25} {score:.0%} {bar}")
                failed += 1

        except Exception as e:
            print(f"  ❌ EXCEPTION: {e}")
            failed += 1

        print()
        print("-" * 70)
        print()

        # Brief pause between tests to avoid rate limiting
        if i < len(TEST_CASES):
            await asyncio.sleep(1)

    # ── FINAL REPORT ──────────────────────────────────────
    print("=" * 70)
    print(f"  RESULTS: {passed}/{len(TEST_CASES)} passed, {failed} failed")
    if ai_wins > 0:
        print(f"  AI advantage: {ai_wins} cases where AI succeeded but keywords would fail")
    print("=" * 70)
    print()

    if failed == 0:
        print("🎉 All tests passed!")
        print()
        print("The zero-shot classification is working correctly.")
        print("Incidents will now be classified by AI, not keyword matching.")
    else:
        print(f"⚠️  {failed} test(s) failed.")
        print()
        print("This is sometimes expected — zero-shot models can disagree with")
        print("our expected answers on ambiguous descriptions. Check the score")
        print("breakdown above to understand the model's reasoning.")
        print()
        print("Common causes of failures:")
        print("  1. HUGGINGFACE_API_KEY not set in .env")
        print("  2. Model fell back to keyword classification (check 'method' field)")
        print("  3. The description is genuinely ambiguous")

    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # asyncio.run() executes the async function from this regular script
    asyncio.run(run_tests())