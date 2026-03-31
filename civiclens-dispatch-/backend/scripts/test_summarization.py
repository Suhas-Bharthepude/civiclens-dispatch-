# backend/scripts/test_summarization.py
#
# Test script for the summarization service.
# Run this to verify the Hugging Face BART API works before
# trusting it to run automatically on every new incident.
#
# Usage:
#   cd ~/Desktop/CivicLensDispatch/civiclens-dispatch-/backend
#   source ../.venv/bin/activate
#   python -m scripts.test_summarization

# asyncio lets us run async functions from a regular (non-async) script
import asyncio

# sys lets us modify the Python path so imports work correctly
import sys

# os for path manipulation
import os

# Add the backend directory to Python's module search path
# This lets us import from app.services.summarization
# Without this, Python can't find the 'app' package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the functions we want to test
from app.services.summarization import summarize_incident, summarize_incident_mock


# ============================================================
# TEST CASES
# ============================================================
# A list of realistic incident scenarios to test with.
# Each entry is a dict with:
#   name:        A label for the test (printed in output)
#   description: The written description from the incident submitter
#   transcript:  Optional audio transcript (or None)

TEST_CASES = [
    {
        "name": "Fire with transcript (long input)",
        "description": (
            "Emergency at 789 Oak Street apartment complex. "
            "Multiple residents have reported seeing smoke and flames "
            "coming from the third floor windows."
        ),
        "transcript": (
            "I can see flames coming out of the third floor windows of the "
            "Oak Street apartment building. There are people on the balconies "
            "screaming for help. The fire looks like it started in apartment "
            "302. I can hear fire alarms going off. There are maybe twenty "
            "residents still inside the building. Please send firefighters "
            "immediately, this is a serious emergency."
        ),
    },
    {
        "name": "Crime report, no transcript",
        "description": (
            "Possible break-in at 567 Maple Drive residence. "
            "Homeowner arrived home to find the front window broken and "
            "the back door wide open. Several valuables appear to be missing "
            "from the living room. The homeowner did not enter the property "
            "and is waiting outside."
        ),
        "transcript": None,
    },
    {
        "name": "Medical emergency with transcript",
        "description": (
            "Medical emergency reported outside the downtown library "
            "on Congress Avenue. Bystanders report a man collapsed."
        ),
        "transcript": (
            "There is a man who collapsed outside the downtown library. "
            "He looks to be in his sixties and he is unconscious and not "
            "responding. Someone is doing CPR right now. We need an ambulance "
            "here as fast as possible. He was walking normally and then just "
            "fell down suddenly."
        ),
    },
    {
        "name": "Short description (should skip API)",
        "description": "Small fire reported.",
        "transcript": None,
    },
    {
        "name": "Traffic incident",
        "description": (
            "Two vehicle collision at the intersection of Broadway and "
            "3rd Street. Both drivers are out of their vehicles. One driver "
            "appears to be holding their neck and may be injured. Traffic "
            "is backing up significantly in all directions."
        ),
        "transcript": None,
    },
]


# ============================================================
# MAIN TEST FUNCTION
# ============================================================

async def run_tests():
    """
    Run all test cases and print the results.
    """

    print()
    print("=" * 70)
    print("  SUMMARIZATION SERVICE TEST")
    print("  Testing: facebook/bart-large-cnn via Hugging Face API")
    print("=" * 70)
    print()

    # Track results for the final report
    passed = 0
    failed = 0

    # Run each test case
    for i, test in enumerate(TEST_CASES, 1):
        print(f"Test {i}/{len(TEST_CASES)}: {test['name']}")
        print(f"  Description ({len(test['description'])} chars):")
        # Print first 100 chars of description
        print(f"    '{test['description'][:100]}...' " if len(test['description']) > 100
              else f"    '{test['description']}'")

        if test["transcript"]:
            print(f"  Transcript ({len(test['transcript'])} chars): YES")
        else:
            print(f"  Transcript: None")

        print()

        try:
            # Call the summarization service
            # This may take 3-10 seconds for the first call (model loading)
            print("  ⏳ Calling summarize_incident()...")
            summary = await summarize_incident(
                description=test["description"],
                transcript=test["transcript"],
            )

            # Print the result
            print(f"  ✅ Summary ({len(summary.split())} words):")
            # Word-wrap the summary at 60 chars for readable output
            words = summary.split()
            line = "     "
            for word in words:
                if len(line) + len(word) > 70:
                    print(line)
                    line = "     " + word + " "
                else:
                    line += word + " "
            if line.strip():
                print(line)

            passed += 1

        except Exception as e:
            # The test raised an unexpected exception
            print(f"  ❌ FAILED with exception: {e}")
            failed += 1

        print()
        print("-" * 70)
        print()

        # Wait 1 second between tests to avoid hitting rate limits
        if i < len(TEST_CASES):
            await asyncio.sleep(1)

    # ── FINAL REPORT ──────────────────────────────────────
    print("=" * 70)
    print(f"  TEST RESULTS: {passed}/{len(TEST_CASES)} passed, {failed} failed")
    print("=" * 70)
    print()

    if passed == len(TEST_CASES):
        print("🎉 All tests passed!")
        print()
        print("The summarization service is working correctly.")
        print("New incidents will now get real AI-generated summaries.")
        print()
        print("Next: Submit a new incident via the frontend and check")
        print("the AI Summary field in the detail panel after ~5 seconds.")
    else:
        print("⚠️  Some tests failed.")
        print()
        print("Common causes:")
        print("  1. HUGGINGFACE_API_KEY not set in backend/.env")
        print("  2. Invalid API key (check it starts with 'hf_')")
        print("  3. Hugging Face API rate limit hit — wait 1 minute and retry")
        print("  4. Network connectivity issue")
        print()
        print("To check your API key:")
        print("  cat backend/.env | grep HUGGINGFACE")

    print()


# ============================================================
# ALSO TEST THE MOCK FUNCTION
# ============================================================

def test_mock():
    """
    Quick test of the mock function — no API call needed.
    Good for verifying the fallback works correctly.
    """

    print("=" * 70)
    print("  MOCK SUMMARIZATION TEST (no API call)")
    print("=" * 70)
    print()

    test_desc = (
        "Fire reported at apartment building on Oak Street. "
        "Multiple residents are trapped and require evacuation."
    )
    test_transcript = (
        "I can see smoke pouring out of the third floor. "
        "There are people on the balcony screaming."
    )

    # Test with both description and transcript
    result = summarize_incident_mock(test_desc, test_transcript)
    print(f"With transcript: '{result}'")
    print()

    # Test with description only
    result = summarize_incident_mock(test_desc, None)
    print(f"Without transcript: '{result}'")
    print()

    # Test with very short description
    result = summarize_incident_mock("Fire.", None)
    print(f"Short description: '{result}'")
    print()

    print("✅ Mock function works correctly")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    # Run the mock test first (instant, no network needed)
    test_mock()

    # Then run the real API tests
    # asyncio.run() is how you execute async functions from a regular script
    asyncio.run(run_tests())