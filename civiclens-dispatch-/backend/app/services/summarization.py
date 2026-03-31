# backend/app/services/summarization.py
#
# AI Summarization Service for CivicLens Dispatch.
# Takes an incident's description and/or audio transcript and produces
# a clear, concise summary paragraph for the dispatcher.
#
# Uses the facebook/bart-large-cnn model via Hugging Face Inference API.
# BART was trained on CNN news articles — ideal for summarizing incident reports
# because news articles and incident reports share the same structure:
# who, what, where, when, how urgent.
#
# Architecture mirrors asr.py exactly:
#   - USE_MOCK_SUMMARIZATION flag controls real vs mock
#   - Mock is used for testing and when API is unavailable
#   - Real function calls Hugging Face with retry logic
#   - incident_processor.py imports and calls summarize_incident()
#
# Day 39: Initial implementation

# asyncio for async/await and sleep between retries
import asyncio

# httpx for making async HTTP requests to Hugging Face
# Same library used by asr.py — already installed
import httpx

# settings gives us the HUGGINGFACE_API_KEY from the .env file
from app.config import settings


# ============================================================
# CONFIGURATION
# ============================================================

# Hugging Face Inference API endpoint for BART summarization model
# facebook/bart-large-cnn is fine-tuned on CNN news articles
# It performs abstractive summarization — writes NEW text, not just excerpts
HF_SUMMARIZATION_URL = (
    "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
)

# If True: use the mock function (fast, no API calls, good for testing)
# If False: call the real Hugging Face API
# Set to True initially — change to False when you want real summaries
# (requires HUGGINGFACE_API_KEY to be set in .env)
USE_MOCK_SUMMARIZATION = False

# Minimum number of words in the combined input text before we bother
# calling the API. BART needs enough text to work with.
# If text is shorter than this, we just clean up the description instead.
MIN_WORDS_FOR_SUMMARY = 30

# Maximum number of words in the generated summary.
# 130 is roughly 2-4 sentences — appropriate for a dispatcher to scan quickly.
MAX_SUMMARY_LENGTH = 130

# Minimum number of words in the generated summary.
# Prevents the model from returning a single-word "summary".
MIN_SUMMARY_LENGTH = 30

# How many times to retry the API call if it fails
# The API can fail due to: model loading (cold start), rate limits, network issues
MAX_RETRIES = 3

# How many seconds to wait between retry attempts
# We increase this each retry (exponential backoff): 2s, 4s, 8s
RETRY_DELAY_SECONDS = 2


# ============================================================
# MOCK SUMMARIZATION (for testing and fallback)
# ============================================================

def summarize_incident_mock(description: str, transcript: str = None) -> str:
    """
    Generate a fake but realistic-looking summary for testing.

    This is used when:
      1. USE_MOCK_SUMMARIZATION is True
      2. The real API call fails (used as fallback)

    Args:
        description: The incident description text written by the submitter
        transcript:  Optional audio transcript text (or None if no audio)

    Returns:
        A mock summary string
    """

    # Combine description and transcript for the mock to work with
    # If no transcript, just use description
    combined = description.strip()
    if transcript and not transcript.startswith("["):
        # Only include transcript if it looks like real text
        # (transcripts starting with "[" are usually error messages)
        combined += " " + transcript.strip()

    # Count words in the combined text
    word_count = len(combined.split())

    # If text is very short, just return the description as-is
    # There's not enough content to "summarize"
    if word_count < 10:
        return description.strip()

    # Build a mock summary based on keywords in the text
    # This mimics what the real model would produce but uses simple rules
    text_lower = combined.lower()

    # Detect the type of incident from keywords
    if any(word in text_lower for word in ["fire", "smoke", "flames", "burning"]):
        incident_context = "fire emergency"
    elif any(word in text_lower for word in ["medical", "injured", "hurt", "ambulance", "unconscious"]):
        incident_context = "medical emergency"
    elif any(word in text_lower for word in ["break", "robbery", "theft", "stolen", "intruder"]):
        incident_context = "crime incident"
    elif any(word in text_lower for word in ["accident", "crash", "collision", "vehicle"]):
        incident_context = "traffic incident"
    elif any(word in text_lower for word in ["flood", "water", "leak", "infrastructure"]):
        incident_context = "infrastructure issue"
    else:
        incident_context = "incident"

    # Use the first 80 characters of the description as a snippet
    # This gives the mock summary some real content
    snippet = description[:80].strip()
    if len(description) > 80:
        # Add ellipsis if we truncated
        snippet += "..."

    # Build and return the mock summary
    # It looks like a real summary but is generated by simple string formatting
    return (
        f"Reported {incident_context}: {snippet} "
        f"{'Audio transcript available. ' if transcript else ''}"
        f"Dispatcher review and appropriate response recommended."
    )


# ============================================================
# REAL SUMMARIZATION (calls Hugging Face API)
# ============================================================

async def _call_summarization_api(input_text: str) -> str:
    """
    Internal function that makes the actual HTTP request to Hugging Face.

    This is separated from summarize_incident() to keep the retry logic clean.
    summarize_incident() calls this function and handles retries.

    Args:
        input_text: The combined description + transcript text to summarize

    Returns:
        The summary text string from the model

    Raises:
        Exception: If the API returns an error or unexpected response format
    """

    # Build the authorization header using the API key from .env
    # Hugging Face expects "Bearer <token>" format
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        # Tell the server we're sending JSON
        "Content-Type": "application/json",
    }

    # Build the request body
    # "inputs" is the text to summarize
    # "parameters" control the output length and generation strategy
    payload = {
        "inputs": input_text,
        "parameters": {
            # Maximum tokens in the output (roughly = words)
            "max_length": MAX_SUMMARY_LENGTH,
            # Minimum tokens — prevents a one-word summary
            "min_length": MIN_SUMMARY_LENGTH,
            # do_sample=False means deterministic output
            # The model always generates the same summary for the same input
            # Set to True for more creative/varied outputs (less predictable)
            "do_sample": False,
        },
        # wait_for_model=True tells Hugging Face to wait if the model
        # is still loading (cold start) instead of returning a 503 error
        "options": {
            "wait_for_model": True,
        },
    }

    # Make the async HTTP POST request
    # timeout=60.0 allows up to 60 seconds for the model to respond
    # Summarization models take longer than simple queries (3-10 seconds)
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HF_SUMMARIZATION_URL,
            headers=headers,
            json=payload,  # httpx serializes the dict to JSON automatically
        )

    # Log the response status for debugging
    print(f"[SUMMARIZATION] API response status: {response.status_code}")

    # Handle model loading (503 = Service Unavailable = model is warming up)
    # This happens on the first call after the model hasn't been used for a while
    if response.status_code == 503:
        # The error body from HF usually says "Model is currently loading"
        raise Exception("Model is loading, will retry")

    # Handle authentication errors
    if response.status_code == 401:
        raise Exception("Invalid Hugging Face API key — check HUGGINGFACE_API_KEY in .env")

    # Handle rate limiting (429 = Too Many Requests)
    if response.status_code == 429:
        raise Exception("Hugging Face rate limit exceeded — wait before retrying")

    # For any other non-200 status, raise an error
    if response.status_code != 200:
        raise Exception(f"API returned status {response.status_code}: {response.text}")

    # Parse the JSON response body
    result = response.json()

    # The response is a list: [{"summary_text": "..."}]
    # Validate the format before accessing it
    if not isinstance(result, list) or len(result) == 0:
        raise Exception(f"Unexpected API response format: {result}")

    if "summary_text" not in result[0]:
        raise Exception(f"Missing 'summary_text' in API response: {result}")

    # Extract and return the summary text
    summary = result[0]["summary_text"].strip()

    # Log a preview of the summary
    print(f"[SUMMARIZATION] Generated summary ({len(summary.split())} words): "
          f"{summary[:80]}...")

    return summary


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

async def summarize_incident(description: str, transcript: str = None) -> str:
    """
    Generate an AI summary of an incident for the dispatcher.

    This is the function that incident_processor.py calls.
    It handles:
      1. Input validation and text construction
      2. Short text detection (skips API for very short descriptions)
      3. Mock vs real API routing based on USE_MOCK_SUMMARIZATION flag
      4. Retry logic for transient API failures
      5. Fallback to mock summary if API fails after all retries

    Args:
        description: The written incident description (required)
                     Example: "There is a fire at 123 Oak Street..."
        transcript:  Optional audio transcript text
                     Example: "Caller reports smoke coming from second floor..."
                     Pass None if no audio was uploaded

    Returns:
        A summary string — either AI-generated or mock
        Never raises an exception (always returns something)

    Example:
        summary = await summarize_incident(
            "Fire reported at apartment building",
            "Caller says flames visible from third floor window"
        )
        # Returns: "Fire emergency at apartment building with visible flames
        #           on the third floor. Immediate fire department response required."
    """

    # Log the start of summarization with useful context
    print(f"[SUMMARIZATION] Starting summarization")
    print(f"[SUMMARIZATION] Description length: {len(description)} chars")
    print(f"[SUMMARIZATION] Has transcript: {transcript is not None}")

    # ── STEP 1: Build the combined input text ────────────
    # Combine description and transcript to give the model maximum context
    if transcript and not transcript.startswith("["):
        # Transcript looks like real text (doesn't start with "[Error..." etc.)
        # Combine with a space separator
        combined_text = f"{description.strip()} {transcript.strip()}"
        print(f"[SUMMARIZATION] Using description + transcript ({len(combined_text)} chars)")
    else:
        # No transcript or transcript is an error message — use description only
        combined_text = description.strip()
        print(f"[SUMMARIZATION] Using description only ({len(combined_text)} chars)")

    # ── STEP 2: Check if text is long enough ─────────────
    word_count = len(combined_text.split())

    if word_count < MIN_WORDS_FOR_SUMMARY:
        # Text is too short for the summarization model to produce good output
        # Return the description as-is (just cleaned up)
        print(f"[SUMMARIZATION] Text too short ({word_count} words < {MIN_WORDS_FOR_SUMMARY} min), "
              f"returning description directly")
        return description.strip()

    print(f"[SUMMARIZATION] Input word count: {word_count} words")

    # ── STEP 3: Use mock if configured ───────────────────
    if USE_MOCK_SUMMARIZATION:
        print("[SUMMARIZATION] Using mock summarization")
        # Call the mock function and return immediately
        return summarize_incident_mock(description, transcript)

    # ── STEP 4: Call real API with retry logic ────────────
    # Try up to MAX_RETRIES times before giving up
    last_error = None  # Store the last error for logging

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[SUMMARIZATION] API attempt {attempt}/{MAX_RETRIES}")

        try:
            # Call the actual Hugging Face API
            summary = await _call_summarization_api(combined_text)

            # Success! Return the summary
            print(f"[SUMMARIZATION] ✅ Summary generated successfully on attempt {attempt}")
            return summary

        except Exception as e:
            # This attempt failed — log the error and decide whether to retry
            last_error = e
            print(f"[SUMMARIZATION] ⚠️  Attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                # Calculate how long to wait before the next attempt
                # Exponential backoff: 2s, 4s, 8s
                # This gives the API time to recover (model loading, rate limits)
                wait_seconds = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                print(f"[SUMMARIZATION] Waiting {wait_seconds}s before retry...")
                await asyncio.sleep(wait_seconds)
            # If this was the last attempt, fall through to the fallback below

    # ── STEP 5: Fallback if all retries failed ────────────
    # We tried MAX_RETRIES times and all failed
    # Rather than crashing the entire incident pipeline, use the mock summary
    # The incident still gets processed — it just gets a less good summary
    print(f"[SUMMARIZATION] ❌ All {MAX_RETRIES} attempts failed. Last error: {last_error}")
    print("[SUMMARIZATION] Falling back to mock summary")

    # Return mock summary as fallback
    return summarize_incident_mock(description, transcript)