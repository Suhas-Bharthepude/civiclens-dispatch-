# backend/app/services/image_analyzer.py
# Image analysis service that uses Hugging Face's DETR object detection model
# to identify objects in uploaded incident photos and build a text description.
#
# This makes CivicLens truly multimodal — it can now process:
#   - Audio (Whisper ASR → transcript)
#   - Text (BART-MNLI → classification, risk; BART-CNN → summary)
#   - Images (DETR → object detection → text description)  ← NEW!
#
# Model: facebook/detr-resnet-50 (via Hugging Face Inference API)
# Method: Object detection — identifies objects and their locations in images
#         Then converts detected objects into a human-readable description
#
# Why object detection instead of image captioning?
# Image captioning models (like BLIP) are not available on the free
# Hugging Face inference tier. Object detection IS available and gives
# useful dispatch-relevant info (e.g., "2 cars, 1 person detected").
#
# Day 48: Real image analysis with a vision model

# Import httpx for making async HTTP requests to the Hugging Face API
import httpx

# Import asyncio for sleep delays during retry logic
import asyncio

# Import os for checking if image files exist on disk
import os

# Import Counter from collections to count how many of each object type
from collections import Counter

# Import settings from our config module for the API key
from app.config import settings


# ========================================
# CONFIGURATION
# ========================================

# The Hugging Face Inference API endpoint for the DETR object detection model
# facebook/detr-resnet-50 detects common objects (people, cars, animals, etc.)
# It returns a list of detected objects with labels, confidence scores, and bounding boxes
# Using the new router.huggingface.co endpoint
IMAGE_MODEL_URL = "https://router.huggingface.co/hf-inference/models/facebook/detr-resnet-50"

# Minimum confidence score to include a detected object (0.0 to 1.0)
# Objects below this threshold are ignored (probably false positives)
# 0.7 means we only keep objects the model is at least 70% sure about
MIN_CONFIDENCE = 0.7

# Maximum number of retries if the model is loading (503 status)
MAX_RETRIES = 5

# Base delay between retries in seconds
BASE_RETRY_DELAY = 5

# Timeout for each API request in seconds
REQUEST_TIMEOUT = 90

# Maximum file size in bytes (5 MB)
# Images larger than this will be skipped to avoid slow uploads
MAX_FILE_SIZE = 5 * 1024 * 1024


# ========================================
# MAIN IMAGE ANALYSIS FUNCTION
# ========================================

async def analyze_image(image_path: str) -> dict:
    """
    Analyze an image using object detection and generate a text description.
    
    This function:
    1. Reads the image file from disk
    2. Sends the raw bytes to DETR object detection via Hugging Face API
    3. Filters results by confidence threshold
    4. Builds a human-readable description from detected objects
    
    Example output: "Objects detected in image: 2 cars, 1 truck (3 objects total)"
    
    Args:
        image_path: Path to the image file on disk
    
    Returns:
        dict with keys:
            - 'caption': str — text description built from detected objects
            - 'method': 'ml' if real model was used, 'fallback'/'error' if not
            - 'file_size': int — size of the image file in bytes
            - 'objects': list — raw detected objects (for potential future use)
    """
    
    # Check if the image file exists on disk
    if not os.path.exists(image_path):
        return {
            "caption": "[Image file not found]",
            "method": "error",
            "file_size": 0,
            "objects": [],
            "reason": f"File not found: {image_path}",
        }
    
    # Get the file size
    file_size = os.path.getsize(image_path)
    
    # Check if the file is too large
    if file_size > MAX_FILE_SIZE:
        return {
            "caption": "[Image too large for analysis]",
            "method": "skipped",
            "file_size": file_size,
            "objects": [],
            "reason": f"File size {file_size} bytes exceeds limit of {MAX_FILE_SIZE} bytes",
        }
    
    # Check if the file is too small (likely corrupt or empty)
    if file_size < 100:
        return {
            "caption": "[Image file appears to be empty or corrupt]",
            "method": "error",
            "file_size": file_size,
            "objects": [],
            "reason": "File size too small — likely corrupt",
        }
    
    # Read the image file as raw bytes
    try:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
    except Exception as e:
        return {
            "caption": f"[Could not read image file: {str(e)}]",
            "method": "error",
            "file_size": file_size,
            "objects": [],
            "reason": str(e),
        }
    
    # Determine the content type based on file extension
    # The API needs to know the image format via Content-Type header
    extension = os.path.splitext(image_path)[1].lower()
    content_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".webp": "image/webp",
    }
    content_type = content_types.get(extension, "image/jpeg")
    
    # Try to call the Hugging Face API
    try:
        result = await _call_detection_api(image_bytes, content_type)
        result["file_size"] = file_size
        return result
    except Exception as e:
        print(f"  ⚠️  ML image analysis failed: {str(e)}")
        print(f"  ⚠️  Returning empty caption")
        return {
            "caption": "[Image analysis unavailable]",
            "method": "fallback",
            "file_size": file_size,
            "objects": [],
            "reason": str(e),
        }


# ========================================
# API CALL WITH RETRY LOGIC
# ========================================

async def _call_detection_api(image_bytes: bytes, content_type: str) -> dict:
    """
    Send image bytes to the Hugging Face DETR object detection API.
    
    The image API sends raw binary data (not JSON).
    The Content-Type header tells the API what format the image is in.
    
    Returns dict with caption, method, and detected objects.
    Raises Exception if all retries are exhausted.
    """
    
    # Build request headers
    # Content-Type MUST be set to the image format — without it the API errors
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}",
        "Content-Type": content_type,
    }
    
    # Retry loop
    for attempt in range(MAX_RETRIES):
        try:
            # Create async HTTP client with timeout
            async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
                # Send POST request with raw image bytes
                # For image APIs, we use content= (raw bytes) not json=
                response = await client.post(
                    IMAGE_MODEL_URL,
                    headers=headers,
                    content=image_bytes
                )
            
            # Handle response
            if response.status_code == 200:
                data = response.json()
                return _parse_detection_response(data)
            
            elif response.status_code == 503:
                wait_time = BASE_RETRY_DELAY * (attempt + 1)
                print(f"  🔄 Image model loading (attempt {attempt + 1}/{MAX_RETRIES}), waiting {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            
            elif response.status_code == 429:
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
                raise Exception("Hugging Face image API timed out after all retries")
        
        except httpx.ConnectError:
            raise Exception("Cannot connect to Hugging Face API — check internet connection")
    
    # All retries exhausted
    raise Exception(f"Hugging Face image API not ready after {MAX_RETRIES} retries")


# ========================================
# PARSE THE DETECTION RESPONSE
# ========================================

def _parse_detection_response(data) -> dict:
    """
    Convert the object detection response into a human-readable caption.
    
    The DETR API returns a list like:
    [
        {"score": 0.98, "label": "car", "box": {"xmin": 0, "ymin": 10, ...}},
        {"score": 0.94, "label": "car", "box": {"xmin": 50, "ymin": 20, ...}},
        {"score": 0.89, "label": "truck", "box": {"xmin": 100, ...}},
    ]
    
    We filter by confidence, count objects, and build a description like:
    "Objects detected in image: 2 cars, 1 truck (3 objects total)"
    
    Returns dict with caption, method, and raw objects list.
    """
    
    # Ensure data is a list
    if not isinstance(data, list):
        raise Exception(f"Unexpected response format: {type(data)}")
    
    # Filter objects by minimum confidence score
    # Only keep detections the model is reasonably sure about
    confident_objects = [
        obj for obj in data
        if obj.get("score", 0) >= MIN_CONFIDENCE
    ]
    
    # If no objects detected with sufficient confidence
    if not confident_objects:
        return {
            "caption": "No distinct objects detected in image",
            "method": "ml",
            "objects": [],
        }
    
    # Count how many of each object type were detected
    # Example: {"car": 2, "truck": 1}
    label_counts = Counter(obj["label"] for obj in confident_objects)
    
    # Build the description string
    # Sort by count descending (most common objects first)
    parts = []
    for label, count in label_counts.most_common():
        if count == 1:
            # Singular: "1 car"
            parts.append(f"1 {label}")
        else:
            # Plural: "2 cars" (simple pluralization by adding 's')
            # This works for most English nouns; edge cases are acceptable
            parts.append(f"{count} {label}s")
    
    # Join the parts with commas
    # Example: "2 cars, 1 truck"
    objects_str = ", ".join(parts)
    
    # Calculate total number of objects
    total = sum(label_counts.values())
    
    # Build the final caption
    caption = f"Objects detected in image: {objects_str} ({total} objects total)"
    
    # Capitalize first letter
    caption = caption[0].upper() + caption[1:]
    
    return {
        "caption": caption,
        "method": "ml",
        "objects": confident_objects,
    }