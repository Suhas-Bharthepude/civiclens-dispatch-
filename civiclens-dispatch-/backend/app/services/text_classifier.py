# backend/app/services/text_classifier.py
# Text classification service that uses Hugging Face zero-shot classification
# to determine incident type (fire, medical, traffic, etc.) and severity (high, medium, low).
#
# This replaces the keyword-based stub from Day 34 which was just:
#   if "fire" in text: incident_type = "fire"
#
# Now the model actually READS the text and classifies it contextually.
#
# Model: facebook/bart-large-mnli (via Hugging Face Inference API)
# Method: Two-pass zero-shot classification (once for type, once for severity)
#
# Day 46: Real ML-based text classification

# Import httpx for making async HTTP requests to the Hugging Face API
# httpx is like 'requests' but supports async/await
import httpx

# Import asyncio for sleep delays during retry logic
import asyncio

# Import settings from our config module
# settings.HUGGINGFACE_API_KEY holds our API token from .env
from app.config import settings


# ========================================
# CONFIGURATION
# ========================================

# The Hugging Face Inference API endpoint for zero-shot classification
# This is the same model we use for risk scoring (Day 45)
# Using the new router.huggingface.co endpoint (old api-inference URL is deprecated)
CLASSIFIER_MODEL_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

# --- INCIDENT TYPE LABELS ---
# These are the categories the model will choose from when classifying incident type
# Each label is written as a natural language description so the model understands it
# The model picks whichever label best matches the meaning of the incident text
USE_MOCK_CLASSIFICATION = False

INCIDENT_TYPE_LABELS = [
    "fire or explosion emergency",                                          # Maps to → "fire"
    "medical emergency or health crisis",                                   # Maps to → "medical"
    "traffic accident or vehicle collision",                                # Maps to → "traffic"
    "criminal activity theft robbery or assault",                           # Maps to → "crime"
    "noise disturbance or noise complaint",                                 # Maps to → "noise"
    "power line electrical outage infrastructure damage utility failure",   # Maps to → "infrastructure"
    "other general matter or miscellaneous issue",                          # Maps to → "other"
]

LABEL_TO_TYPE = {
    "fire or explosion emergency": "fire",
    "medical emergency or health crisis": "medical",
    "traffic accident or vehicle collision": "traffic",
    "criminal activity theft robbery or assault": "crime",
    "noise disturbance or noise complaint": "noise",
    "power line electrical outage infrastructure damage utility failure": "infrastructure",
    "other general matter or miscellaneous issue": "other",
}

# --- SEVERITY LABELS ---
# These are the severity levels the model will choose from
# Written as natural language descriptions for the model to understand
SEVERITY_LABELS = [
    "critical high severity life-threatening emergency requiring immediate response",
    "moderate severity situation requiring attention but not immediately dangerous",
    "minor low severity non-urgent issue that can be handled routinely",
]

# Mapping from severity labels to the short severity names in our database
LABEL_TO_SEVERITY = {
    "critical high severity life-threatening emergency requiring immediate response": "high",
    "moderate severity situation requiring attention but not immediately dangerous": "medium",
    "minor low severity non-urgent issue that can be handled routinely": "low",
}

# Keywords that override the ML severity classification when present.
# The ML model (BART-large-mnli) is reliable for incident TYPE but often
# under-estimates severity for extreme descriptions. These lists patch that gap.
CRITICAL_SEVERITY_KEYWORDS = [
    "unresponsive", "no pulse", "not breathing", "cardiac arrest", "cpr",
    "explosion", "explosions", "spreading to adjacent", "engulfed",
    "trapped", "fatality", "fatalities", "life-threatening",
    "sparking", "downed power line", "downed line", "power line",
    "multiple casualties", "mass casualty",
]

LOW_SEVERITY_KEYWORDS = [
    "noise complaint", "loud music", "noise disturbance",
    "pothole", "graffiti", "non-urgent", "barking dog",
]

# Maximum number of retries if the model is loading (503 status)
MAX_RETRIES = 4

# Base delay between retries in seconds (increases with each attempt)
BASE_RETRY_DELAY = 5

# Maximum text length to send to the model (characters)
# Longer text doesn't necessarily improve classification accuracy
MAX_TEXT_LENGTH = 1500

# Timeout for each API request in seconds
REQUEST_TIMEOUT = 60


# ========================================
# MAIN CLASSIFICATION FUNCTION
# ========================================

async def classify_incident(text: str) -> dict:
    """
    Classify incident text to determine incident type and severity.
    
    This function makes TWO separate API calls:
    1. First call: Determine incident type (fire, medical, traffic, etc.)
    2. Second call: Determine severity (high, medium, low)
    
    We use two separate calls because each needs different candidate labels.
    The model can only pick from one set of labels per request.
    
    Args:
        text: The incident text to classify (description + transcript combined)
    
    Returns:
        dict with keys:
            - 'incident_type': str like "fire", "medical", "traffic", etc.
            - 'severity': str like "high", "medium", "low"
            - 'type_confidence': float (0.0-1.0) confidence in the type classification
            - 'severity_confidence': float (0.0-1.0) confidence in the severity
            - 'method': 'ml' if real model was used, 'fallback' if keyword-based
    """
    
    # Truncate text if it's too long
    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH]
    
    # Clean the text - remove extra whitespace
    text = " ".join(text.split())
    
    # If text is too short to classify meaningfully, return defaults
    if len(text.strip()) < 10:
        return {
            "incident_type": "other",
            "severity": "medium",
            "type_confidence": 0.0,
            "severity_confidence": 0.0,
            "method": "fallback",
            "reason": "Text too short for meaningful classification",
        }
    
    try:
        # --- PASS 1: Classify incident type ---
        # Send the text with incident type labels
        type_result = await _call_zero_shot_api(text, INCIDENT_TYPE_LABELS)
        
        # Find the label with the highest confidence score
        # The API returns results sorted by confidence, highest first
        top_type_label = type_result[0]["label"]
        top_type_confidence = type_result[0]["score"]
        
        # Map the natural language label to our short database type name
        # Example: "fire or explosion emergency" → "fire"
        incident_type = LABEL_TO_TYPE.get(top_type_label, "other")
        
        # --- PASS 2: Classify severity ---
        # Send the text with severity labels
        severity_result = await _call_zero_shot_api(text, SEVERITY_LABELS)

        # Find the label with the highest confidence
        top_severity_label = severity_result[0]["label"]
        top_severity_confidence = severity_result[0]["score"]

        # Map to our short database severity name
        severity = LABEL_TO_SEVERITY.get(top_severity_label, "medium")

        # Override with keyword check — ML underestimates severity for extreme text
        severity = _apply_severity_keywords(text, severity)

        # Return the classification results
        return {
            "incident_type": incident_type,
            "severity": severity,
            "type_confidence": round(top_type_confidence, 4),
            "severity_confidence": round(top_severity_confidence, 4),
            "method": "ml",
        }
    
    except Exception as e:
        # If ML classification fails, fall back to keyword-based classification
        print(f"  ⚠️  ML classification failed: {str(e)}")
        print(f"  ⚠️  Falling back to keyword-based classification")
        return _fallback_classification(text)


# ========================================
# SEVERITY KEYWORD OVERRIDE
# ========================================

def _apply_severity_keywords(text: str, ml_severity: str) -> str:
    """
    Override ML severity when unambiguous critical or low keywords are present.
    BART-large-mnli reliably classifies incident type but tends to underestimate
    severity for extreme descriptions, so we patch the result here.
    """
    text_lower = text.lower()
    for kw in CRITICAL_SEVERITY_KEYWORDS:
        if kw in text_lower:
            return "high"
    if ml_severity != "high":
        for kw in LOW_SEVERITY_KEYWORDS:
            if kw in text_lower:
                return "low"
    return ml_severity


# ========================================
# API CALL WITH RETRY LOGIC
# ========================================

async def _call_zero_shot_api(text: str, candidate_labels: list) -> list:
    """
    Call the Hugging Face zero-shot classification API.
    
    This is the same pattern as risk_scorer.py but generalized
    to accept any set of candidate labels.
    
    Args:
        text: The text to classify
        candidate_labels: List of label strings the model picks from
    
    Returns:
        List of dicts like [{"label": "...", "score": 0.85}, ...]
        sorted by score descending (highest confidence first).
    
    Raises:
        Exception if all retries are exhausted.
    """
    
    # Build request headers with our API key
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build the request payload for zero-shot classification
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": candidate_labels,
        }
    }
    
    # Retry loop
    for attempt in range(MAX_RETRIES):
        try:
            # Create async HTTP client with timeout
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                # Send POST request to the Hugging Face API
                response = await client.post(
                    CLASSIFIER_MODEL_URL,
                    headers=headers,
                    json=payload
                )
            
            # Handle response based on status code
            if response.status_code == 200:
                # Success - parse the response
                data = response.json()
                
                # The new router API returns a list of {label, score} dicts
                # Example: [{"label": "fire or explosion", "score": 0.82}, ...]
                if isinstance(data, list):
                    # Sort by score descending (highest confidence first)
                    # The API usually returns them sorted, but we sort to be safe
                    return sorted(data, key=lambda x: x["score"], reverse=True)
                elif isinstance(data, dict):
                    # Old format compatibility: {labels: [...], scores: [...]}
                    labels = data.get("labels", [])
                    scores = data.get("scores", [])
                    result = [{"label": l, "score": s} for l, s in zip(labels, scores)]
                    return sorted(result, key=lambda x: x["score"], reverse=True)
                else:
                    raise Exception(f"Unexpected response format: {type(data)}")
            
            elif response.status_code == 503:
                # Model is loading - wait and retry
                wait_time = BASE_RETRY_DELAY * (attempt + 1)
                print(f"  🔄 Model loading (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            
            elif response.status_code == 429:
                # Rate limited - wait longer and retry
                wait_time = BASE_RETRY_DELAY * (attempt + 2)
                print(f"  🔄 Rate limited (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            
            elif response.status_code == 401:
                raise Exception("Hugging Face API key is invalid (401 Unauthorized)")
            
            else:
                raise Exception(f"Hugging Face API returned status {response.status_code}: {response.text[:200]}")
        
        except httpx.TimeoutException:
            if attempt < MAX_RETRIES - 1:
                print(f"  🔄 Request timed out (attempt {attempt + 1}/{MAX_RETRIES}), retrying...")
                await asyncio.sleep(BASE_RETRY_DELAY)
                continue
            else:
                raise Exception("Hugging Face API timed out after all retries")
        
        except httpx.ConnectError:
            raise Exception("Cannot connect to Hugging Face API - check internet connection")
    
    # All retries exhausted
    raise Exception(f"Hugging Face API not ready after {MAX_RETRIES} retries")


# ========================================
# FALLBACK: KEYWORD-BASED CLASSIFICATION
# ========================================

def _fallback_classification(text: str) -> dict:
    """
    Simple keyword-based classification as a fallback when ML model is unavailable.
    
    This is the same logic from the original Day 34 stub, preserved as a safety net.
    Uses keyword matching to guess incident type and severity.
    
    Returns dict with incident_type, severity, confidences, and method='fallback'.
    """
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Check keywords for each incident type
    # Order matters — check most specific/dangerous types first
    if "fire" in text_lower or "smoke" in text_lower or "burn" in text_lower or "explosion" in text_lower:
        incident_type = "fire"
        severity = "high"
    elif "medical" in text_lower or "injured" in text_lower or "hurt" in text_lower or "bleeding" in text_lower or "unconscious" in text_lower:
        incident_type = "medical"
        severity = "high"
    elif "accident" in text_lower or "crash" in text_lower or "collision" in text_lower or "vehicle" in text_lower:
        incident_type = "traffic"
        severity = "medium"
    elif "break" in text_lower or "robbery" in text_lower or "theft" in text_lower or "steal" in text_lower or "assault" in text_lower or "shooting" in text_lower:
        incident_type = "crime"
        severity = "high"
    elif "noise" in text_lower or "complaint" in text_lower or "loud" in text_lower or "music" in text_lower:
        incident_type = "noise"
        severity = "low"
    elif "water" in text_lower or "flood" in text_lower or "leak" in text_lower or "pothole" in text_lower or "streetlight" in text_lower:
        incident_type = "infrastructure"
        severity = "medium"
    else:
        incident_type = "other"
        severity = "medium"
    
    return {
        "incident_type": incident_type,
        "severity": severity,
        "type_confidence": 0.0,
        "severity_confidence": 0.0,
        "method": "fallback",
        "reason": "ML model unavailable, used keyword-based classification",
    }