# backend/app/services/classification.py
#
# AI Text Classification Service for CivicLens Dispatch.
# Classifies incident text into a type (fire, medical, crime, etc.)
# and determines severity (low, medium, high, critical).
#
# Uses zero-shot classification via facebook/bart-large-mnli on Hugging Face.
# "Zero-shot" means the model classifies text into ANY categories you give it
# without needing to be specifically trained on those categories first.
#
# How it works:
#   You give the model text + a list of candidate labels.
#   The model returns confidence scores for each label.
#   The label with the highest score is the classification.
#
# Example:
#   Input:  "The building is engulfed in flames"
#   Labels: ["fire emergency", "medical emergency", ...]
#   Output: fire emergency = 0.94, medical emergency = 0.03, ...
#   Result: "fire" with 94% confidence
#
# Day 40: Initial implementation
# Fixed: router.huggingface.co returns list of {label, score} dicts,
#        not the old {labels: [], scores: []} format.

# asyncio for async/await and sleep between retries
import asyncio

# httpx for making async HTTP requests to Hugging Face
import httpx

# settings gives us HUGGINGFACE_API_KEY from .env
from app.config import settings


# ============================================================
# CONFIGURATION
# ============================================================

# Hugging Face Inference API endpoint for zero-shot classification
# bart-large-mnli is fine-tuned on Multi-Genre Natural Language Inference —
# this training makes it excellent at zero-shot classification
HF_CLASSIFICATION_URL = (
    "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"
)

# Set to True to use mock (fast, no API calls, good for testing)
# Set to False to use the real Hugging Face API
USE_MOCK_CLASSIFICATION = False

# The candidate labels we send to the zero-shot classifier.
# Using descriptive phrases ("fire emergency") rather than single words ("fire")
# gives the model more context and produces better results.
INCIDENT_LABELS = [
    "fire emergency",          # fires, smoke, burning buildings
    "medical emergency",       # injuries, unconscious, ambulance needed
    "criminal activity",       # break-ins, theft, assault, robbery
    "traffic accident",        # vehicle collisions, road incidents
    "infrastructure problem",  # potholes, flooding, utility issues
    "other incident",          # anything that doesn't fit above
]

# Mapping from the verbose label the API returns to the short type
# string stored in the database
LABEL_TO_TYPE = {
    "fire emergency":         "fire",
    "medical emergency":      "medical",
    "criminal activity":      "crime",
    "traffic accident":       "traffic",
    "infrastructure problem": "infrastructure",
    "other incident":         "other",
}

# Minimum confidence (0.0–1.0) required to use the AI result.
# If below this, fall back to keyword matching.
# 0.35 is intentionally low — zero-shot on short text rarely hits 0.9+
CONFIDENCE_THRESHOLD = 0.35

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2

# Words that upgrade severity to "critical" regardless of incident type
CRITICAL_KEYWORDS = [
    "trapped", "unconscious", "not breathing", "spreading",
    "armed", "shooting", "shots fired", "explosion",
    "collapsed", "overdose", "unresponsive",
]

# Words that upgrade "medium" severity to "high"
URGENT_KEYWORDS = [
    "emergency", "urgent", "immediate", "serious", "critical",
    "help", "danger", "threatening", "bleeding", "fire",
]


# ============================================================
# SEVERITY LOGIC
# ============================================================

def determine_severity(incident_type: str, text: str) -> str:
    """
    Determine severity level based on incident type and text content.

    Args:
        incident_type: The classified type string (e.g., "fire")
        text:          The full incident text to check for urgency keywords

    Returns:
        One of: "low", "medium", "high", "critical"
    """

    # Lowercase for case-insensitive keyword checking
    text_lower = text.lower()

    # Base severity per incident type
    base_severity_map = {
        "fire":           "high",
        "medical":        "high",
        "crime":          "high",
        "traffic":        "medium",
        "infrastructure": "low",
        "other":          "medium",
    }

    severity = base_severity_map.get(incident_type, "medium")

    # Check for critical keywords — upgrade to critical immediately
    for keyword in CRITICAL_KEYWORDS:
        if keyword in text_lower:
            return "critical"

    # Check for urgent keywords — upgrade medium → high
    if severity == "medium":
        for keyword in URGENT_KEYWORDS:
            if keyword in text_lower:
                severity = "high"
                break

    return severity


# ============================================================
# KEYWORD FALLBACK CLASSIFIER
# ============================================================

def classify_by_keywords(text: str) -> dict:
    """
    Simple keyword-based classification used as fallback when:
      - The AI API is unavailable
      - AI confidence is below the threshold
      - USE_MOCK_CLASSIFICATION is True

    Args:
        text: The incident text to classify

    Returns:
        Classification result dict with the same keys as the AI classifier
    """

    text_lower = text.lower()

    # Check keywords in order — more specific checks first
    if any(w in text_lower for w in ["fire", "smoke", "flames", "burning",
                                      "engulfed", "ablaze"]):
        incident_type = "fire"
    elif any(w in text_lower for w in ["medical", "injured", "hurt", "ambulance",
                                        "unconscious", "bleeding", "fell",
                                        "collapsed", "breathing", "overdose",
                                        "seizure", "responding"]):
        incident_type = "medical"
    elif any(w in text_lower for w in ["shots", "shooting", "gunshot", "armed",
                                        "weapon", "break", "robbery", "theft",
                                        "stolen", "assault", "attacked",
                                        "trespassing", "forced"]):
        incident_type = "crime"
    elif any(w in text_lower for w in ["accident", "crash", "collision", "vehicle",
                                        "car", "truck", "motorcycle",
                                        "intersection", "collided"]):
        incident_type = "traffic"
    elif any(w in text_lower for w in ["pothole", "flood", "leak", "water main",
                                        "power out", "road", "infrastructure",
                                        "streetlight", "sewage", "hole in"]):
        incident_type = "infrastructure"
    else:
        incident_type = "other"

    severity = determine_severity(incident_type, text)

    return {
        "incident_type": incident_type,
        "severity":      severity,
        "confidence":    0.0,
        "method":        "keyword_fallback",
        "top_scores":    {},
    }


# ============================================================
# MOCK CLASSIFIER (for testing)
# ============================================================

async def classify_incident_mock(text: str) -> dict:
    """
    Mock classification for testing without API calls.
    Uses keyword fallback but labels the method as "mock".
    """
    print("[CLASSIFICATION] Using mock classification")
    result = classify_by_keywords(text)
    result["method"] = "mock"
    return result


# ============================================================
# REAL API CALL
# ============================================================

async def _call_classification_api(text: str) -> dict:
    """
    Makes the HTTP request to Hugging Face and returns
    {"labels": [...], "scores": [...]} regardless of which
    response format the API uses.

    The router.huggingface.co API returns a list of {label, score} dicts:
      [{"label": "fire emergency", "score": 0.97}, ...]
    The old api-inference endpoint returned:
      [{"labels": [...], "scores": [...]}]
    We handle both so the rest of the code works either way.

    Args:
        text: The incident text to classify

    Returns:
        {"labels": [...], "scores": [...]} — sorted by score descending

    Raises:
        Exception on API errors or unexpected response format
    """

    # Authorization header using the API key from .env
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }

    # Request body for zero-shot classification
    payload = {
        "inputs": text,
        "parameters": {
            # The categories the model chooses from
            "candidate_labels": INCIDENT_LABELS,
            # False = pick exactly ONE label (scores sum to 1.0)
            "multi_label": False,
        },
        "options": {
            # Wait for model to load rather than returning 503 on cold start
            "wait_for_model": True,
        },
    }

    # Make the async POST request (60 second timeout)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HF_CLASSIFICATION_URL,
            headers=headers,
            json=payload,
        )

    print(f"[CLASSIFICATION] API response status: {response.status_code}")

    # Handle known error codes
    if response.status_code == 503:
        raise Exception("Model is loading, will retry")
    if response.status_code == 401:
        raise Exception("Invalid Hugging Face API key — check HUGGINGFACE_API_KEY in .env")
    if response.status_code == 429:
        raise Exception("Hugging Face rate limit exceeded")
    if response.status_code != 200:
        raise Exception(f"API returned status {response.status_code}: {response.text}")

    # Parse the JSON response body
    result = response.json()

    # Validate we got a non-empty list
    if not isinstance(result, list) or len(result) == 0:
        raise Exception(f"Unexpected API response format: {result}")

    # ── Handle response format ────────────────────────────
    # router.huggingface.co (NEW): list of individual {label, score} dicts
    #   [{"label": "fire emergency", "score": 0.97}, {"label": "other", "score": 0.01}]
    #
    # api-inference.huggingface.co (OLD): single dict with parallel arrays
    #   [{"labels": ["fire emergency", ...], "scores": [0.97, ...]}]

    if "label" in result[0] and "score" in result[0]:
        # New router format — convert to parallel arrays
        labels = [item["label"] for item in result]
        scores = [item["score"] for item in result]

    elif "labels" in result[0] and "scores" in result[0]:
        # Old format — already parallel arrays
        labels = result[0]["labels"]
        scores = result[0]["scores"]

    else:
        # Unknown format — raise so retry logic can handle it
        raise Exception(f"Unexpected API response format: {result}")

    # Return as a simple dict with parallel lists
    # Already sorted by score descending (highest confidence first)
    return {"labels": labels, "scores": scores}


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

async def classify_incident(description: str, transcript: str = None) -> dict:
    """
    Classify an incident into a type and severity using AI.

    Called by incident_processor.py for every new incident.

    Args:
        description: The written incident description (required)
        transcript:  Optional audio transcript text (or None)

    Returns:
        {
            "incident_type": str,   # "fire", "medical", "crime", etc.
            "severity":      str,   # "low", "medium", "high", "critical"
            "confidence":    float, # 0.0–1.0
            "method":        str,   # "ai", "keyword_fallback", or "mock"
            "top_scores":    dict,  # all labels and scores for debugging
        }

    Never raises — always returns a valid result.
    """

    print("[CLASSIFICATION] Starting classification")
    print(f"[CLASSIFICATION] Description length: {len(description)} chars")
    print(f"[CLASSIFICATION] Has transcript: {transcript is not None}")

    # ── Build combined input text ─────────────────────────
    # More context = better classification
    if transcript and not transcript.startswith("["):
        combined_text = f"{description.strip()} {transcript.strip()}"
        print(f"[CLASSIFICATION] Using description + transcript ({len(combined_text)} chars)")
    else:
        combined_text = description.strip()
        print(f"[CLASSIFICATION] Using description only ({len(combined_text)} chars)")

    # ── Use mock if configured ────────────────────────────
    if USE_MOCK_CLASSIFICATION:
        return await classify_incident_mock(combined_text)

    # ── Call real API with retry logic ────────────────────
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[CLASSIFICATION] API attempt {attempt}/{MAX_RETRIES}")

        try:
            # Call the API — returns {"labels": [...], "scores": [...]}
            api_response = await _call_classification_api(combined_text)

            # Unpack the parallel lists
            labels = api_response["labels"]  # e.g. ["fire emergency", "other", ...]
            scores = api_response["scores"]  # e.g. [0.94, 0.01, ...]

            # Top prediction is first (already sorted by score descending)
            top_label = labels[0]   # e.g. "fire emergency"
            top_score = scores[0]   # e.g. 0.94

            print(f"[CLASSIFICATION] Top: '{top_label}' ({top_score:.2%} confidence)")

            # Build score dict for debugging
            # zip() pairs each label with its score
            top_scores = dict(zip(labels, scores))

            # ── Confidence threshold check ────────────────
            # If the model isn't confident enough, use keyword fallback
            if top_score < CONFIDENCE_THRESHOLD:
                print(f"[CLASSIFICATION] Confidence {top_score:.2%} below "
                      f"threshold {CONFIDENCE_THRESHOLD:.0%} — using keyword fallback")
                result = classify_by_keywords(combined_text)
                # Still include AI scores so we can see what the model thought
                result["top_scores"] = top_scores
                return result

            # ── Convert label to database type string ─────
            # "fire emergency" → "fire"
            incident_type = LABEL_TO_TYPE.get(top_label, "other")

            # ── Determine severity ────────────────────────
            severity = determine_severity(incident_type, combined_text)

            print(f"[CLASSIFICATION] ✅ type={incident_type}, severity={severity}, "
                  f"confidence={top_score:.2%}, method=ai")

            return {
                "incident_type": incident_type,
                "severity":      severity,
                "confidence":    round(top_score, 4),
                "method":        "ai",
                "top_scores":    top_scores,
            }

        except Exception as e:
            last_error = e
            print(f"[CLASSIFICATION] ⚠️  Attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                # Exponential backoff: 2s, 4s, 8s
                wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                print(f"[CLASSIFICATION] Waiting {wait}s before retry...")
                await asyncio.sleep(wait)

    # ── All retries failed — use keyword fallback ─────────
    print(f"[CLASSIFICATION] ❌ All {MAX_RETRIES} attempts failed: {last_error}")
    print("[CLASSIFICATION] Falling back to keyword classification")
    return classify_by_keywords(combined_text)