# backend/app/services/image_analysis.py
#
# AI Image Analysis Service for CivicLens Dispatch.
# Analyzes photos uploaded with incident reports and produces
# a natural language description of what the image shows.
#
# Uses image captioning via Salesforce/blip-image-captioning-large
# on Hugging Face. BLIP (Bootstrapping Language-Image Pre-training)
# was trained on 129 million image-text pairs and produces accurate,
# readable descriptions of photographs.
#
# Example:
#   Input:  photo of a car crash
#   Output: "two vehicles involved in a collision at an intersection,
#            one car has significant front-end damage"
#
# Architecture mirrors asr.py, summarization.py, and classification.py:
#   - USE_MOCK flag for testing without API calls
#   - Mock function for fast testing
#   - Real function sends image bytes to Hugging Face
#   - incident_processor.py imports and calls analyze_image()
#
# Day 42: Initial implementation

# asyncio for async/await and sleep between retries
import asyncio

# httpx for making async HTTP requests to Hugging Face
import httpx

# Path for working with file paths (checking extensions, reading files)
from pathlib import Path

# settings gives us HUGGINGFACE_API_KEY from .env
from app.config import settings


# ============================================================
# CONFIGURATION
# ============================================================

# Hugging Face Inference API endpoint for BLIP image captioning
# blip-image-captioning-large is the standard-sized BLIP model
# It produces one sentence describing the image content
HF_IMAGE_CAPTION_URL = (
    "https://router.huggingface.co/hf-inference/models/"
    "Salesforce/blip-image-captioning-large"
)

# Set to True to use mock (no API calls, instant results)
# Set to False to use the real Hugging Face API
USE_MOCK_IMAGE_ANALYSIS = True

# How many times to retry the API call if it fails
MAX_RETRIES = 3

# Base delay between retries in seconds (doubles each attempt)
RETRY_DELAY_SECONDS = 2

# Map of file extensions to MIME content types
# Used to set the correct Content-Type header when sending images
# The API needs to know what format it's receiving
IMAGE_CONTENT_TYPES = {
    "jpg":  "image/jpeg",
    "jpeg": "image/jpeg",
    "png":  "image/png",
    "heic": "image/heic",
    "heif": "image/heif",
    "webp": "image/webp",
    "gif":  "image/gif",
}


# ============================================================
# HELPER: Get Content-Type for an image file
# ============================================================

def get_image_content_type(image_path: str) -> str:
    """
    Determine the MIME content type from the image file extension.

    Args:
        image_path: Path to the image file (e.g., "media/tmp/images/abc.jpg")

    Returns:
        MIME type string (e.g., "image/jpeg")
        Defaults to "image/jpeg" if extension is unrecognized
    """

    # Extract just the file extension (e.g., "jpg" from "photo.jpg")
    # .suffix returns ".jpg" so we strip the dot with [1:]
    extension = Path(image_path).suffix.lower().lstrip(".")

    # Look up the MIME type, default to image/jpeg if unknown
    return IMAGE_CONTENT_TYPES.get(extension, "image/jpeg")


# ============================================================
# MOCK IMAGE ANALYSIS (for testing)
# ============================================================

async def analyze_image_mock(image_path: str) -> str:
    """
    Generate a fake image description for testing without API calls.

    Args:
        image_path: Path to the image file (used only for logging)

    Returns:
        A realistic-looking mock image description string
    """

    print(f"[IMAGE] Using mock image analysis for: {Path(image_path).name}")

    # Simulate a small delay so it feels like a real API call
    await asyncio.sleep(0.5)

    # Return a generic description that looks like a real caption
    # In real use this would be unique to each image
    return (
        "a street scene showing an incident area with emergency response vehicles "
        "present and bystanders observing from a safe distance"
    )


# ============================================================
# REAL IMAGE ANALYSIS (calls Hugging Face API)
# ============================================================

async def _call_image_caption_api(image_path: str) -> str:
    """
    Internal function that reads the image file and calls the
    Hugging Face BLIP captioning API.

    Sends raw image bytes with the correct Content-Type header.
    The API returns a caption describing what's in the image.

    Args:
        image_path: Full path to the image file on disk

    Returns:
        Caption string describing the image

    Raises:
        FileNotFoundError: If the image file doesn't exist
        Exception: On API errors
    """

    # ── STEP 1: Validate the file exists ─────────────────
    path = Path(image_path)

    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Get file size for logging
    file_size_kb = path.stat().st_size / 1024
    print(f"[IMAGE] File: {path.name} ({file_size_kb:.1f} KB)")

    # ── STEP 2: Read the image as binary bytes ────────────
    # "rb" means "read binary" — reads raw bytes, not text
    # We need raw bytes because images are not text files
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    print(f"[IMAGE] Read {len(image_bytes):,} bytes from file")

    # ── STEP 3: Determine the Content-Type header ─────────
    # The API needs to know what image format it's receiving
    content_type = get_image_content_type(image_path)
    print(f"[IMAGE] Content-Type: {content_type}")

    # ── STEP 4: Build the request headers ────────────────
    headers = {
        # Authorization with our Hugging Face API key
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        # Tell the API what image format we're sending
        "Content-Type": content_type,
    }

    # ── STEP 5: Send the request ──────────────────────────
    # We send the raw image bytes directly as the request body
    # This is different from JSON requests — no json= parameter,
    # we use content= to send raw bytes
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            HF_IMAGE_CAPTION_URL,
            headers=headers,
            content=image_bytes,  # raw bytes, not JSON
        )

    print(f"[IMAGE] API response status: {response.status_code}")

    # ── STEP 6: Handle errors ─────────────────────────────
    if response.status_code == 503:
        raise Exception("Model is loading, will retry")

    if response.status_code == 401:
        raise Exception("Invalid Hugging Face API key")

    if response.status_code == 429:
        raise Exception("Hugging Face rate limit exceeded")

    if response.status_code != 200:
        raise Exception(f"API returned status {response.status_code}: {response.text}")

    # ── STEP 7: Parse the response ────────────────────────
    result = response.json()

    # BLIP returns: [{"generated_text": "a description of the image"}]
    # It's a list with one item — we extract the generated_text field
    if not isinstance(result, list) or len(result) == 0:
        raise Exception(f"Unexpected API response format: {result}")

    if "generated_text" not in result[0]:
        raise Exception(f"Missing 'generated_text' in API response: {result}")

    # Extract the caption text and strip whitespace
    caption = result[0]["generated_text"].strip()

    print(f"[IMAGE] Caption: '{caption}'")

    return caption


# ============================================================
# MAIN PUBLIC FUNCTION
# ============================================================

async def analyze_image(image_path: str) -> str:
    """
    Analyze an uploaded image and return a text description.

    This is the function that incident_processor.py calls.
    It handles:
      1. Mock vs real API routing
      2. Retry logic for transient failures
      3. Fallback to a generic description if all retries fail

    Args:
        image_path: Path to the image file on disk
                    (stored in incidents.image_path in the database)

    Returns:
        A string describing the image content.
        Always returns something — never raises an exception.

    Example:
        description = await analyze_image("media/tmp/images/abc.jpg")
        # Returns: "two vehicles involved in a collision at an intersection"
    """

    print(f"[IMAGE] Starting image analysis: {image_path}")

    # ── Use mock if configured ────────────────────────────
    if USE_MOCK_IMAGE_ANALYSIS:
        return await analyze_image_mock(image_path)

    # ── Call real API with retry logic ────────────────────
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        print(f"[IMAGE] API attempt {attempt}/{MAX_RETRIES}")

        try:
            # Call the BLIP captioning API
            caption = await _call_image_caption_api(image_path)

            print(f"[IMAGE] ✅ Analysis complete on attempt {attempt}")
            return caption

        except Exception as e:
            last_error = e
            print(f"[IMAGE] ⚠️  Attempt {attempt} failed: {e}")

            if attempt < MAX_RETRIES:
                # Exponential backoff: 2s, 4s, 8s
                wait = RETRY_DELAY_SECONDS * (2 ** (attempt - 1))
                print(f"[IMAGE] Waiting {wait}s before retry...")
                await asyncio.sleep(wait)

    # ── All retries failed — return generic fallback ──────
    print(f"[IMAGE] ❌ All {MAX_RETRIES} attempts failed: {last_error}")
    print("[IMAGE] Returning generic fallback description")

    # Return a generic description rather than crashing the pipeline
    # The incident still gets processed even if image analysis fails
    return "Image uploaded — automated analysis unavailable. Manual review recommended."