# backend/app/services/summarizer.py
# Summarization service that uses Hugging Face's BART-Large-CNN model
# to generate concise, human-readable summaries of incident text.
#
# This replaces the template-based stub from Day 34 which was:
#   summary = f"{incident_type} incident. {description[:50]}... Audio transcript available."
#
# Now the model actually READS the text and writes a real summary.
#
# Model: facebook/bart-large-cnn (via Hugging Face Inference API)
# Method: Abstractive summarization (generates new text, doesn't just extract sentences)
#
# Day 47: Real ML-based summarization — the LAST stub replaced!

# Import httpx for making async HTTP requests to the Hugging Face API
import httpx

# Import asyncio for sleep delays during retry logic
import asyncio

# Import settings from our config module for the API key
from app.config import settings


# ========================================
# CONFIGURATION
# ========================================

# The Hugging Face Inference API endpoint for the summarization model
# facebook/bart-large-cnn is trained on CNN/DailyMail news articles
# News articles are structurally similar to incident reports (events, details, outcomes)
# Using the new router.huggingface.co endpoint (old api-inference URL is deprecated)
SUMMARIZER_MODEL_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"

# Maximum number of retries if the model is loading (503 status)
# bart-large-cnn is a big model and may take longer to load than bart-large-mnli
MAX_RETRIES = 5

# Base delay between retries in seconds
BASE_RETRY_DELAY = 5

# Maximum number of characters to send to the model
# BART-Large-CNN has a token limit of ~1024 tokens (~3000-4000 chars)
# Sending more than this will cause the API to truncate or error
MAX_INPUT_LENGTH = 3000

# Minimum input length to attempt summarization (characters)
# If the text is shorter than this, summarization is pointless —
# the "summary" would be as long as the original
MIN_INPUT_LENGTH = 80

# Parameters for the generated summary
# These control how long the output summary should be (in tokens, roughly words)
SUMMARY_MIN_LENGTH = 20   # Summary must be at least ~20 words
SUMMARY_MAX_LENGTH = 100  # Summary should be at most ~100 words

# Timeout for each API request in seconds
# Summarization takes longer than classification because the model generates text
REQUEST_TIMEOUT = 90


# ========================================
# MAIN SUMMARIZATION FUNCTION
# ========================================

async def summarize_text(text: str) -> dict:
    """
    Generate a concise summary of incident text using BART-Large-CNN.
    
    This function:
    1. Checks if text is long enough to be worth summarizing
    2. Sends text to the BART-Large-CNN model via Hugging Face API
    3. Returns the generated summary
    
    Args:
        text: The incident text to summarize (description + transcript combined)
    
    Returns:
        dict with keys:
            - 'summary': str — the generated summary text
            - 'method': 'ml' if real model was used, 'fallback' if template-based
            - 'input_length': int — character count of the input text
            - 'output_length': int — character count of the generated summary
    """
    
    # Clean the text — remove extra whitespace and newlines
    text = " ".join(text.split())
    
    # Check if text is long enough to summarize
    # If the original text is very short, there's nothing to summarize —
    # the summary would just be the same text repeated
    if len(text.strip()) < MIN_INPUT_LENGTH:
        return {
            "summary": text.strip(),
            "method": "passthrough",
            "input_length": len(text),
            "output_length": len(text),
            "reason": "Text too short to summarize — returned as-is",
        }
    
    # Truncate text if it's too long for the model
    # BART-Large-CNN can handle ~1024 tokens, which is roughly 3000 characters
    if len(text) > MAX_INPUT_LENGTH:
        text = text[:MAX_INPUT_LENGTH]
    
    # Try to call the Hugging Face API
    try:
        result = await _call_summarization_api(text)
        return result
    
    except Exception as e:
        # If the API fails, fall back to simple template-based summary
        print(f"  ⚠️  ML summarization failed: {str(e)}")
        print(f"  ⚠️  Falling back to template-based summary")
        return _fallback_summary(text)


# ========================================
# API CALL WITH RETRY LOGIC
# ========================================

async def _call_summarization_api(text: str) -> dict:
    """
    Call the Hugging Face summarization API with retry logic.
    
    The summarization endpoint is different from the classification endpoint:
    - Input: raw text (not a JSON object with candidate_labels)
    - Output: generated summary text
    - Parameters: min_length, max_length control summary size
    
    Returns dict with summary, method, and lengths.
    Raises Exception if all retries are exhausted.
    """
    
    # Build request headers
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        "Content-Type": "application/json",
    }
    
    # Build the request payload for summarization
    # 'inputs' is the text to summarize
    # 'parameters' control the output length
    payload = {
        "inputs": text,
        "parameters": {
            "min_length": SUMMARY_MIN_LENGTH,    # At least ~20 words
            "max_length": SUMMARY_MAX_LENGTH,    # At most ~100 words
            "do_sample": False,                  # Use greedy decoding (deterministic)
            # do_sample=False means the model always picks the most likely next word
            # This gives consistent, reliable summaries (same input → same output)
            # do_sample=True would add randomness (different each time)
        }
    }
    
    # Retry loop
    for attempt in range(MAX_RETRIES):
        try:
            # Create async HTTP client with timeout
            # Summarization takes longer than classification, so we use a longer timeout
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                # Send POST request to the summarization endpoint
                response = await client.post(
                    SUMMARIZER_MODEL_URL,
                    headers=headers,
                    json=payload
                )
            
            # Handle response based on status code
            if response.status_code == 200:
                # Success — parse the response
                data = response.json()
                return _parse_summarization_response(data, text)
            
            elif response.status_code == 503:
                # Model is loading — bart-large-cnn is a large model
                # First load can take 30-60 seconds on free tier
                wait_time = BASE_RETRY_DELAY * (attempt + 1)
                print(f"  🔄 Summarization model loading (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            
            elif response.status_code == 429:
                # Rate limited
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
                raise Exception("Hugging Face summarization API timed out after all retries")
        
        except httpx.ConnectError:
            raise Exception("Cannot connect to Hugging Face API — check internet connection")
    
    # All retries exhausted
    raise Exception(f"Hugging Face summarization API not ready after {MAX_RETRIES} retries")


# ========================================
# PARSE THE SUMMARIZATION RESPONSE
# ========================================

def _parse_summarization_response(data, original_text: str) -> dict:
    """
    Extract the summary text from the API response.
    
    The summarization API returns either:
    - A list: [{"summary_text": "The summary..."}]      (old format)
    - A list: [{"generated_text": "The summary..."}]     (alternate format)
    - A dict: {"summary_text": "The summary..."}         (less common)
    
    We handle all formats for robustness.
    
    Returns dict with summary, method, and lengths.
    """
    
    # Extract the summary text from the response
    summary_text = ""
    
    if isinstance(data, list) and len(data) > 0:
        # Most common format: list with one dict
        first_item = data[0]
        
        if isinstance(first_item, dict):
            # Try 'summary_text' key first (standard summarization response)
            summary_text = first_item.get("summary_text", "")
            
            # If not found, try 'generated_text' (alternate key name)
            if not summary_text:
                summary_text = first_item.get("generated_text", "")
        
        elif isinstance(first_item, str):
            # Sometimes the response is just a list of strings
            summary_text = first_item
    
    elif isinstance(data, dict):
        # Less common: direct dict response
        summary_text = data.get("summary_text", "")
        if not summary_text:
            summary_text = data.get("generated_text", "")
    
    # If we still don't have a summary, something went wrong
    if not summary_text:
        raise Exception(f"Could not extract summary from API response: {str(data)[:200]}")
    
    # Clean up the summary text
    # Remove leading/trailing whitespace
    summary_text = summary_text.strip()
    
    # Return the result
    return {
        "summary": summary_text,
        "method": "ml",
        "input_length": len(original_text),
        "output_length": len(summary_text),
    }


# ========================================
# FALLBACK: TEMPLATE-BASED SUMMARIZATION
# ========================================

def _fallback_summary(text: str) -> dict:
    """
    Simple template-based summary as a fallback when the ML model is unavailable.
    
    This is the same approach from the original Day 34 stub.
    Takes the first portion of the text and adds ellipsis.
    
    Not ideal, but ensures every incident gets SOME summary even during API outages.
    
    Returns dict with summary, method, and lengths.
    """
    
    # Take the first 150 characters of the text as a basic summary
    # Add ellipsis if the text was longer
    if len(text) > 150:
        summary = text[:150].rsplit(" ", 1)[0] + "..."
        # rsplit(" ", 1)[0] splits at the last space before 150 chars
        # This avoids cutting a word in the middle
    else:
        summary = text
    
    return {
        "summary": summary,
        "method": "fallback",
        "input_length": len(text),
        "output_length": len(summary),
        "reason": "ML model unavailable, used text truncation",
    }