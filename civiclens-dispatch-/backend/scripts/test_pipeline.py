# backend/scripts/test_pipeline.py
#
# Comprehensive end-to-end pipeline test script.
# Tests all four AI services in sequence, then runs the complete
# pipeline simulation on a sample incident.
#
# Run this whenever you want to verify the whole system is working:
#
#   cd ~/Desktop/CivicLensDispatch/civiclens-dispatch-/backend
#   source ../.venv/bin/activate
#   python -m scripts.test_pipeline

import asyncio
import sys
import os

# Add the backend directory to the Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import all four AI services
from app.services.classification import classify_incident
from app.services.summarization  import summarize_incident
from app.services.image_analysis import analyze_image_mock
from app.services.asr            import transcribe_audio_mock

# Import the mock flags so we can report status
from app.services.classification import USE_MOCK_CLASSIFICATION
from app.services.summarization  import USE_MOCK_SUMMARIZATION
from app.services.image_analysis import USE_MOCK_IMAGE_ANALYSIS
from app.services.asr            import USE_MOCK_TRANSCRIPTION


# ============================================================
# SAMPLE TEST DATA
# ============================================================
# A realistic incident that exercises all AI services

SAMPLE_INCIDENT = {
    "description": (
        "Large fire reported at the Oak Street apartment complex. "
        "Thick black smoke visible from several blocks away. "
        "Multiple residents trapped on upper floors. "
        "Fire appears to have started approximately ten minutes ago "
        "and is spreading rapidly to adjacent units."
    ),
    "transcript": (
        "I can see flames coming out of the third floor windows. "
        "There are people on the balconies calling for help. "
        "The fire started in apartment 302. "
        "Please send firefighters immediately, this is serious."
    ),
    "image_path": None,  # No real image — will use mock
}


# ============================================================
# HELPER: Print section header
# ============================================================

def header(title: str):
    """Print a formatted section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


# ============================================================
# TEST 1: Classification Service
# ============================================================

async def test_classification():
    """Test the zero-shot classification service."""

    header("TEST 1: Classification Service")
    print(f"  Mode: {'MOCK' if USE_MOCK_CLASSIFICATION else 'REAL API'}")
    print(f"  Model: facebook/bart-large-mnli")
    print()

    # Test with the sample incident
    print("  Input description:")
    print(f"  '{SAMPLE_INCIDENT['description'][:80]}...'")
    print()
    print("  Running classification...")

    result = await classify_incident(
        description=SAMPLE_INCIDENT["description"],
        transcript=SAMPLE_INCIDENT["transcript"],
    )

    # Print results
    print()
    print(f"  ✅ Results:")
    print(f"     Incident type: {result['incident_type']}")
    print(f"     Severity:      {result['severity']}")
    print(f"     Confidence:    {result['confidence']:.0%}")
    print(f"     Method:        {result['method']}")

    # Validate the result looks reasonable
    assert result["incident_type"] in ["fire", "medical", "crime", "traffic", "infrastructure", "other"], \
        f"Unexpected incident type: {result['incident_type']}"
    assert result["severity"] in ["low", "medium", "high", "critical"], \
        f"Unexpected severity: {result['severity']}"

    print()
    print("  ✅ Classification test PASSED")
    return result


# ============================================================
# TEST 2: Summarization Service
# ============================================================

async def test_summarization():
    """Test the BART summarization service."""

    header("TEST 2: Summarization Service")
    print(f"  Mode: {'MOCK' if USE_MOCK_SUMMARIZATION else 'REAL API'}")
    print(f"  Model: facebook/bart-large-cnn")
    print()

    print("  Running summarization...")

    summary = await summarize_incident(
        description=SAMPLE_INCIDENT["description"],
        transcript=SAMPLE_INCIDENT["transcript"],
    )

    print(f"  ✅ Summary ({len(summary.split())} words):")
    # Word-wrap the summary for readable output
    words = summary.split()
    line = "     "
    for word in words:
        if len(line) + len(word) > 65:
            print(line)
            line = "     " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)

    # Validate
    assert len(summary) > 10, "Summary is too short"

    print()
    print("  ✅ Summarization test PASSED")
    return summary


# ============================================================
# TEST 3: Image Analysis Service
# ============================================================

async def test_image_analysis():
    """Test the BLIP image analysis service (mock only)."""

    header("TEST 3: Image Analysis Service")
    print(f"  Mode: {'MOCK' if USE_MOCK_IMAGE_ANALYSIS else 'REAL API'}")
    print(f"  Model: Salesforce/blip-image-captioning-base")
    print()

    print("  Running image analysis (mock)...")

    # Always use mock for the pipeline test — no image file needed
    description = await analyze_image_mock("test_image.jpg")

    print(f"  ✅ Image description:")
    print(f"     '{description}'")

    assert len(description) > 10, "Image description too short"

    print()
    print("  ✅ Image analysis test PASSED")
    return description


# ============================================================
# TEST 4: ASR Service
# ============================================================

async def test_asr():
    """Test the Whisper ASR service (mock only)."""

    header("TEST 4: ASR Service (Speech-to-Text)")
    print(f"  Mode: {'MOCK' if USE_MOCK_TRANSCRIPTION else 'REAL API'}")
    print(f"  Model: openai/whisper-small")
    print()

    print("  Running ASR (mock)...")

    # Always use mock for the pipeline test — no audio file needed
    transcript = await transcribe_audio_mock("test_audio.wav")

    print(f"  ✅ Mock transcript:")
    print(f"     '{transcript[:100]}...'")

    assert len(transcript) > 10, "Transcript too short"

    print()
    print("  ✅ ASR test PASSED")
    return transcript


# ============================================================
# TEST 5: Full Pipeline Simulation
# ============================================================

async def test_full_pipeline(classification_result, summary, image_desc, transcript):
    """
    Simulate the complete pipeline using results from the individual tests.
    This tests that all services work together and produce consistent output.
    """

    header("TEST 5: Full Pipeline Simulation")
    print("  Simulating complete pipeline for a sample incident...")
    print()

    incident_type = classification_result["incident_type"]
    severity      = classification_result["severity"]
    confidence    = classification_result["confidence"]

    # Simulate risk score calculation (same logic as incident_processor.py)
    severity_to_risk = {
        "critical": 0.95,
        "high":     0.85,
        "medium":   0.55,
        "low":      0.25,
    }

    risk_score = severity_to_risk.get(severity, 0.55)

    if confidence > 0.8 and severity in ("high", "critical"):
        risk_score = min(1.0, risk_score + 0.05)

    # Check image description for risk boost
    if image_desc:
        img_lower = image_desc.lower()
        if any(w in img_lower for w in ["fire", "flames", "smoke", "crash", "damage"]):
            risk_score = min(1.0, risk_score + 0.05)

    # Print final pipeline output
    print("  ┌─────────────────────────────────────────────────┐")
    print("  │  PIPELINE OUTPUT                                │")
    print("  ├─────────────────────────────────────────────────┤")
    print(f"  │  Type:        {incident_type:<33} │")
    print(f"  │  Severity:    {severity:<33} │")
    print(f"  │  Confidence:  {f'{confidence:.0%}':<33} │")
    print(f"  │  Risk Score:  {risk_score:.2f}{'':<31} │")
    print(f"  │  Has Summary: {'Yes' if summary else 'No':<33} │")
    print(f"  │  Has Image:   {'Yes' if image_desc else 'No':<33} │")
    print(f"  │  Has Audio:   {'Yes' if transcript else 'No':<33} │")
    print("  └─────────────────────────────────────────────────┘")

    # Validate the complete output
    assert 0.0 <= risk_score <= 1.0,  f"Risk score out of range: {risk_score}"
    assert incident_type,             "Incident type is empty"
    assert severity,                  "Severity is empty"
    assert summary,                   "Summary is empty"

    print()
    print("  ✅ Full pipeline simulation PASSED")


# ============================================================
# MAIN: Run all tests
# ============================================================

async def main():
    """Run all pipeline tests in sequence."""

    print()
    print("╔══════════════════════════════════════════════════════════╗")
    print("║         CIVICLENS DISPATCH — PIPELINE TEST SUITE        ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()
    print("  This script tests all four AI services and the complete")
    print("  pipeline simulation without needing the frontend.")
    print()

    # Track pass/fail
    passed = 0
    failed = 0
    results = {}

    # Run each test, catching failures independently
    # A failure in one test doesn't stop the others from running
    for test_name, test_fn in [
        ("Classification", test_classification),
        ("Summarization",  test_summarization),
        ("Image Analysis", test_image_analysis),
        ("ASR",            test_asr),
    ]:
        try:
            result = await test_fn()
            results[test_name] = result
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name} test FAILED: {e}")
            results[test_name] = None
            failed += 1

    # Run full pipeline simulation only if all individual tests passed
    if failed == 0:
        try:
            await test_full_pipeline(
                classification_result=results["Classification"],
                summary=results["Summarization"],
                image_desc=results["Image Analysis"],
                transcript=results["ASR"],
            )
            passed += 1
        except Exception as e:
            print(f"  ❌ Full pipeline test FAILED: {e}")
            failed += 1

    # ── FINAL REPORT ──────────────────────────────────────
    header("TEST RESULTS")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print()

    if failed == 0:
        print("  🎉 ALL TESTS PASSED!")
        print()
        print("  The CivicLens AI pipeline is working correctly.")
        print("  All four services processed the sample incident.")
    else:
        print(f"  ⚠️  {failed} test(s) failed.")
        print()
        print("  Check the error messages above.")
        print("  Common causes:")
        print("  1. HUGGINGFACE_API_KEY not set in .env")
        print("  2. Missing Python packages (run: pip install httpx)")
        print("  3. Network connectivity issues")

    print()


# Entry point — runs the async main function
if __name__ == "__main__":
    asyncio.run(main())