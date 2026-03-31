# backend/scripts/test_image_analysis.py
#
# Test script for the image analysis service.
# Downloads a few test images from the web and runs them
# through the BLIP captioning API.
#
# Usage:
#   cd ~/Desktop/CivicLensDispatch/civiclens-dispatch-/backend
#   source ../.venv/bin/activate
#   python -m scripts.test_image_analysis

import asyncio
import sys
import os
import tempfile

# Add backend to Python path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# httpx to download test images
import httpx

# The service we're testing
from app.services.image_analysis import analyze_image, analyze_image_mock


# ============================================================
# TEST IMAGE URLS
# ============================================================
# These are publicly available images we'll download and analyze.
# Using real photos tests the model more thoroughly than synthetic images.

TEST_IMAGES = [
    {
        "name": "Street intersection",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a7/Camponotus_flavomarginatus_ant.jpg/320px-Camponotus_flavomarginatus_ant.jpg",
        # We use this as a test regardless of content — we just need any image
    },
    {
        "name": "Local test image (if exists)",
        "url": None,  # Will try to find a local image instead
    },
]


# ============================================================
# HELPER: Download a test image to a temp file
# ============================================================

async def download_test_image(url: str) -> str:
    """
    Download an image from a URL and save it to a temporary file.

    Args:
        url: The URL of the image to download

    Returns:
        Path to the downloaded temporary file

    Raises:
        Exception if download fails
    """
    print(f"  Downloading test image...")

    # Download the image
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to download image: HTTP {response.status_code}")

    # Determine file extension from Content-Type header
    content_type = response.headers.get("content-type", "image/jpeg")
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png":  ".png",
        "image/gif":  ".gif",
        "image/webp": ".webp",
    }
    ext = ext_map.get(content_type.split(";")[0].strip(), ".jpg")

    # Save to a temporary file
    # NamedTemporaryFile creates a file that's deleted when we're done
    tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
    tmp.write(response.content)
    tmp.close()

    print(f"  Saved to: {tmp.name} ({len(response.content):,} bytes)")
    return tmp.name


# ============================================================
# HELPER: Find a local image for testing
# ============================================================

def find_local_test_image() -> str:
    """
    Try to find a local image file to use for testing.
    Looks in the media/tmp/images directory.

    Returns:
        Path to a local image file, or None if none found
    """
    images_dir = "app/media/tmp/images"

    if not os.path.exists(images_dir):
        return None

    # Look for any image file in the directory
    for filename in os.listdir(images_dir):
        if filename.lower().endswith((".jpg", ".jpeg", ".png", ".heic")):
            full_path = os.path.join(images_dir, filename)
            print(f"  Found local image: {filename}")
            return full_path

    return None


# ============================================================
# MAIN TEST FUNCTION
# ============================================================

async def run_tests():
    """
    Run image analysis tests.
    """

    print()
    print("=" * 70)
    print("  IMAGE ANALYSIS SERVICE TEST")
    print("  Testing: Salesforce/blip-image-captioning-base via Hugging Face")
    print("=" * 70)
    print()

    # ── TEST 1: Mock function ─────────────────────────────
    print("Test 1: Mock image analysis (no API call)")
    print("-" * 40)

    mock_result = await analyze_image_mock("test_image.jpg")
    print(f"Mock result: '{mock_result}'")
    print("✅ Mock function works")
    print()

    # ── TEST 2: Local image (if available) ────────────────
    print("Test 2: Local image from media/tmp/images/")
    print("-" * 40)

    local_path = find_local_test_image()

    if local_path:
        print(f"  Testing with: {local_path}")
        try:
            result = await analyze_image(local_path)
            print(f"✅ Caption: '{result}'")
        except Exception as e:
            print(f"❌ Failed: {e}")
    else:
        print("  No local images found in app/media/tmp/images/")
        print("  Submit an incident with a photo to create a test image,")
        print("  then re-run this script.")
    print()

    # ── TEST 3: Downloaded test image ─────────────────────
    print("Test 3: Downloaded test image from Wikipedia")
    print("-" * 40)

    test_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"

    tmp_path = None
    try:
        # Download the image
        tmp_path = await download_test_image(test_url)

        # Run analysis
        print(f"  Running BLIP analysis...")
        result = await analyze_image(tmp_path)
        print(f"✅ Caption: '{result}'")

    except Exception as e:
        print(f"❌ Failed: {e}")
        print("  Common causes:")
        print("  1. HUGGINGFACE_API_KEY not set in .env")
        print("  2. Network connectivity issue")
        print("  3. Hugging Face API rate limit hit")

    finally:
        # Clean up the temporary file
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)
            print(f"  Cleaned up temp file: {tmp_path}")

    print()
    print("=" * 70)
    print("  TEST COMPLETE")
    print("=" * 70)
    print()
    print("Next: Submit an incident with a photo via the frontend")
    print("and check the 'Image Description' field in the detail panel.")
    print()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    asyncio.run(run_tests())