# backend/app/services/risk_scorer.py
# Risk scoring service that uses Hugging Face zero-shot classification
# to analyze incident text and produce a 0.0 to 1.0 urgency score.
#
# This replaces the stub risk scoring from Day 34 which was just:
#   if severity == "high": risk_score = 0.85
#
# Now the model actually READS the text and determines urgency.
#
# Model: facebook/bart-large-mnli (via Hugging Face Inference API)
# Method: Zero-shot classification with urgency labels
#
# Day 45: Real ML-based risk scoring

# Import httpx for making async HTTP requests to the Hugging Face API
# httpx is like 'requests' but supports async/await
# We installed this on Day 33 for the ASR service
import httpx

# Import asyncio for sleep delays during retry logic
import asyncio

# Import os to read environment variables (API key)
import os

# Import settings from our config module
# settings.HUGGINGFACE_API_KEY holds our API token from .env
from app.config import settings


# ========================================
# CONFIGURATION
# ========================================

# The Hugging Face Inference API endpoint for the zero-shot classification model
# facebook/bart-large-mnli is a model trained on natural language inference
# It can classify text into ANY categories you define (zero-shot = no training needed)
# Updated March 2026: Hugging Face migrated from api-inference.huggingface.co
# to router.huggingface.co - the old URL returns 410 Gone
RISK_MODEL_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-mnli"

# These are the urgency labels we ask the model to classify text into
# The model will return a confidence score (0.0 to 1.0) for each label
# We chose these labels to cover the full spectrum of emergency urgency
URGENCY_LABELS = [
    "critical life-threatening emergency",   # Score weight: 1.0 (most urgent)
    "high urgency dangerous situation",      # Score weight: 0.8
    "moderate concern requires attention",   # Score weight: 0.5
    "low priority non-urgent matter",        # Score weight: 0.2
    "routine informational report",          # Score weight: 0.0 (least urgent)
]

# Weights that map each label to a risk score contribution
# Index 0 = "critical life-threatening emergency" → weight 1.0
# Index 4 = "routine informational report" → weight 0.0
# These weights determine how each label's confidence affects the final score
LABEL_WEIGHTS = [1.0, 0.8, 0.5, 0.2, 0.0]

# Maximum number of times to retry if the model is loading (503 status)
# Hugging Face free tier models go to sleep after inactivity
# First request "wakes them up" which takes 20-30 seconds
MAX_RETRIES = 4

# How long to wait between retries (in seconds)
# We increase this each retry (exponential backoff)
BASE_RETRY_DELAY = 5

# Maximum number of characters to send to the model
# Very long text can slow down or fail the API call
# 1500 chars is enough context for urgency assessment
MAX_TEXT_LENGTH = 1500

# Timeout for each API request in seconds
# If the API doesn't respond in 30 seconds, we give up on that attempt
REQUEST_TIMEOUT = 30


# ========================================
# MAIN RISK SCORING FUNCTION
# ========================================

async def calculate_risk_score(text: str) -> dict:
    """
    Analyze incident text and return a risk score between 0.0 and 1.0.
    
    This function:
    1. Sends the text to facebook/bart-large-mnli via Hugging Face API
    2. Gets back confidence scores for each urgency label
    3. Converts those into a single weighted risk score
    4. Returns the score plus the raw label confidences
    
    Args:
        text: The incident text to analyze (description + transcript combined)
    
    Returns:
        dict with keys:
            - 'score': float between 0.0 (routine) and 1.0 (critical emergency)
            - 'labels': dict mapping each urgency label to its confidence
            - 'method': 'ml' if real model was used, 'fallback' if rule-based
    """
    
    # Truncate text if it's too long
    # Very long text wastes API time and doesn't improve accuracy much
    # The first 1500 characters usually contain the most important info
    if len(text) > MAX_TEXT_LENGTH:
        # Cut at MAX_TEXT_LENGTH and note that we truncated
        text = text[:MAX_TEXT_LENGTH]
    
    # Clean the text - remove extra whitespace and newlines
    # Models work better with clean, single-spaced text
    text = " ".join(text.split())
    
    # If text is empty or very short, return a default medium score
    # Can't meaningfully classify "hi" or an empty string
    if len(text.strip()) < 10:
        return {
            "score": 0.5,
            "labels": {},
            "method": "fallback",
            "reason": "Text too short for meaningful classification"
        }
    
    # Try to call the Hugging Face API with retry logic
    # The model might be loading (503) on the first request
    try:
        # Call the internal function that handles the API request and retries
        result = await _call_zero_shot_api(text)
        return result
    
    except Exception as e:
        # If all retries fail, fall back to simple rule-based scoring
        # This ensures incidents always get SOME score, even if the API is down
        print(f"  ⚠️  ML risk scoring failed: {str(e)}")
        print(f"  ⚠️  Falling back to rule-based scoring")
        return _fallback_risk_score(text)


# ========================================
# API CALL WITH RETRY LOGIC
# ========================================

async def _call_zero_shot_api(text: str) -> dict:
    """
    Call the Hugging Face zero-shot classification API with retry logic.
    
    Handles:
    - 503 responses (model is loading, need to wait and retry)
    - 429 responses (rate limited, need to slow down)
    - Timeout errors (network issues)
    - Unexpected errors (API changes, bad responses)
    
    Returns dict with score, labels, and method.
    Raises Exception if all retries are exhausted.
    """
    
    # Build the request headers
    # Authorization header tells Hugging Face who we are
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build the request payload for zero-shot classification
    # 'inputs' is the text to classify
    # 'parameters.candidate_labels' is the list of categories to choose from
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": URGENCY_LABELS,
        }
    }
    
    # Retry loop - try up to MAX_RETRIES times
    for attempt in range(MAX_RETRIES):
        try:
            # Create an async HTTP client with a timeout
            # 'async with' ensures the client is properly closed after use
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                
                # Make the POST request to the Hugging Face API
                # This sends our text and urgency labels to the model
                response = await client.post(
                    RISK_MODEL_URL,
                    headers=headers,
                    json=payload
                )
            
            # Check the response status code
            if response.status_code == 200:
                # Success - parse the response and calculate score
                data = response.json()
                return _parse_classification_response(data)
            
            elif response.status_code == 503:
                # Model is loading - this is normal for free tier
                # The model goes to sleep after 15 minutes of inactivity
                # We need to wait for it to wake up (usually 20-30 seconds)
                wait_time = BASE_RETRY_DELAY * (attempt + 1)
                print(f"  🔄 Model loading (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                # Continue to next iteration of the retry loop
                continue
            
            elif response.status_code == 429:
                # Rate limited - we're sending too many requests
                # Wait longer before trying again
                wait_time = BASE_RETRY_DELAY * (attempt + 2)
                print(f"  🔄 Rate limited (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            
            elif response.status_code == 401:
                # Authentication failed - bad API key
                # No point retrying, the key is wrong
                raise Exception("Hugging Face API key is invalid (401 Unauthorized)")
            
            else:
                # Some other error status code
                raise Exception(f"Hugging Face API returned status {response.status_code}: {response.text[:200]}")
        
        except httpx.TimeoutException:
            # Request took too long - network might be slow
            if attempt < MAX_RETRIES - 1:
                print(f"  🔄 Request timed out (attempt {attempt + 1}/{MAX_RETRIES}), retrying...")
                await asyncio.sleep(BASE_RETRY_DELAY)
                continue
            else:
                raise Exception("Hugging Face API timed out after all retries")
        
        except httpx.ConnectError:
            # Can't reach the API at all - network issue
            raise Exception("Cannot connect to Hugging Face API - check internet connection")
    
    # If we get here, all retries were exhausted (503s or 429s)
    raise Exception(f"Hugging Face API not ready after {MAX_RETRIES} retries")


# ========================================
# PARSE THE API RESPONSE INTO A RISK SCORE
# ========================================

def _parse_classification_response(data) -> dict:
    """
    Convert the zero-shot classification response into a risk score.
    
    The router.huggingface.co API returns a list of dicts like:
    [
        {"label": "critical life-threatening emergency", "score": 0.72},
        {"label": "high urgency dangerous situation", "score": 0.15},
        ...
    ]
    
    We convert this into a single 0.0-1.0 score using weighted sum:
    score = sum(label_confidence * label_weight) for each label
    
    Returns dict with score, labels, and method.
    """
    
    # The new Hugging Face router API returns a list of {label, score} dicts
    # The old API returned {labels: [...], scores: [...]} — that format is deprecated
    # We handle both formats for safety
    
    # Build a dictionary mapping label text to confidence score
    # Example: {"critical life-threatening emergency": 0.72, "high urgency...": 0.15, ...}
    label_confidences = {}
    
    if isinstance(data, list):
        # New format from router.huggingface.co (March 2026+)
        # Each item is {"label": "some label", "score": 0.72}
        for item in data:
            label_confidences[item["label"]] = round(item["score"], 4)
    elif isinstance(data, dict):
        # Old format from api-inference.huggingface.co (deprecated)
        # {"labels": [...], "scores": [...]}
        response_labels = data.get("labels", [])
        response_scores = data.get("scores", [])
        for label, score in zip(response_labels, response_scores):
            label_confidences[label] = round(score, 4)
    
    # Calculate the weighted risk score
    # For each urgency label, multiply its confidence by its weight
    # Then sum all the products to get the final score
    #
    # Example:
    #   "critical emergency" confidence=0.72 * weight=1.0 = 0.72
    #   "high urgency"       confidence=0.15 * weight=0.8 = 0.12
    #   "moderate concern"   confidence=0.08 * weight=0.5 = 0.04
    #   "low priority"       confidence=0.03 * weight=0.2 = 0.006
    #   "routine"            confidence=0.02 * weight=0.0 = 0.0
    #   Total weighted score = 0.72 + 0.12 + 0.04 + 0.006 + 0.0 = 0.886
    weighted_score = 0.0
    
    for i, label in enumerate(URGENCY_LABELS):
        # Get the confidence for this label from the API response
        # Default to 0.0 if the label wasn't in the response (shouldn't happen)
        confidence = label_confidences.get(label, 0.0)
        
        # Get the weight for this label's position
        weight = LABEL_WEIGHTS[i]
        
        # Add the weighted contribution to the total score
        weighted_score += confidence * weight
    
    # Clamp the score to the 0.0-1.0 range
    # Should already be in range since confidences sum to 1.0 and weights are 0.0-1.0
    # But clamping is a safety measure against floating point edge cases
    final_score = max(0.0, min(1.0, round(weighted_score, 4)))
    
    # Return the result as a structured dictionary
    return {
        "score": final_score,
        "labels": label_confidences,
        "method": "ml",
    }


# ========================================
# FALLBACK: RULE-BASED RISK SCORING
# ========================================

def _fallback_risk_score(text: str) -> dict:
    """
    Simple rule-based risk scoring as a fallback when the ML model is unavailable.
    
    This is the same logic from the original stub, but organized as a proper fallback.
    Uses keyword matching to estimate urgency.
    
    This ensures incidents always get a score, even if:
    - Hugging Face API is down
    - API key is expired
    - Network issues prevent API calls
    - Rate limits are hit
    
    Returns dict with score, labels (empty), and method='fallback'.
    """
    
    # Convert text to lowercase for case-insensitive keyword matching
    text_lower = text.lower()
    
    # Start with a base score of 0.3 (slightly below medium)
    # This is the "we don't know" default
    score = 0.3
    
    # Check for critical emergency keywords
    # These words strongly suggest life-threatening situations
    critical_keywords = ["fire", "explosion", "shooting", "stabbing", "trapped",
                         "collapse", "bomb", "active shooter", "hostage"]
    for keyword in critical_keywords:
        if keyword in text_lower:
            # Each critical keyword adds 0.25 to the score
            score += 0.25
            # Stop after first match to avoid over-boosting
            break
    
    # Check for high urgency keywords
    # These suggest serious situations needing prompt response
    high_keywords = ["injured", "bleeding", "unconscious", "accident", "crash",
                     "assault", "robbery", "medical", "ambulance", "emergency"]
    for keyword in high_keywords:
        if keyword in text_lower:
            score += 0.20
            break
    
    # Check for moderate concern keywords
    # These suggest situations that need attention but aren't emergencies
    moderate_keywords = ["broken", "damage", "hazard", "suspicious", "threat",
                         "flood", "leak", "smoke", "alarm"]
    for keyword in moderate_keywords:
        if keyword in text_lower:
            score += 0.10
            break
    
    # Check for urgency/distress language
    # Words that indicate the caller is panicked or situation is time-sensitive
    urgency_words = ["help", "please", "hurry", "urgent", "immediately", "dying",
                     "screaming", "panic"]
    for word in urgency_words:
        if word in text_lower:
            score += 0.10
            break
    
    # Check for low-priority indicators
    # These suggest non-emergency situations
    low_keywords = ["noise", "parking", "complaint", "graffiti", "pothole",
                    "streetlight", "litter", "barking"]
    for keyword in low_keywords:
        if keyword in text_lower:
            # Reduce the score for non-emergency situations
            score -= 0.15
            break
    
    # Clamp the final score to 0.0-1.0 range
    # The keyword additions/subtractions could push it out of bounds
    final_score = max(0.0, min(1.0, round(score, 4)))
    
    return {
        "score": final_score,
        "labels": {},
        "method": "fallback",
        "reason": "ML model unavailable, used keyword-based scoring"
    }