# backend/scripts/test_image_analyzer.py
# Test script for the image analysis service
# Run this BEFORE integrating into the pipeline to verify the model works
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   python scripts/test_image_analyzer.py
#
# IMPORTANT: You need at least one image file to test with.
# The script will look for images in app/media/tmp/images/
# If no images exist there, it will create a simple test image.
#
# Day 48: Image analysis service testing

# Import asyncio to run async functions
import asyncio

# Import sys and os for path fixing
import sys
import os

# Add the backend directory to Python's path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our image analysis function
from app.services.image_analyzer import analyze_image


# ========================================
# HELPER: CREATE A TEST IMAGE IF NEEDED
# ========================================

def create_test_image(path: str):
    """
    Create a simple test image (a small red square) for testing.
    This is a minimal valid JPEG file — just enough for the API to accept it.
    If you have real incident photos, those will give better captions.
    """
    try:
        # Try to create a simple image using basic bytes
        # This creates a tiny 2x2 pixel BMP image (simplest format)
        # BMP header for a 2x2 pixel, 24-bit color image
        import struct
        
        # BMP file header (14 bytes)
        file_header = struct.pack('<2sIHHI',
            b'BM',      # Signature
            70,          # File size (14 + 40 + 16 bytes of pixel data)
            0,           # Reserved
            0,           # Reserved
            54           # Offset to pixel data
        )
        
        # BMP info header (40 bytes)
        info_header = struct.pack('<IiiHHIIiiII',
            40,          # Header size
            2,           # Width (2 pixels)
            2,           # Height (2 pixels)
            1,           # Color planes
            24,          # Bits per pixel (24 = RGB)
            0,           # Compression (none)
            16,          # Image size (2*2*3 + padding = 16)
            2835,        # Horizontal resolution
            2835,        # Vertical resolution
            0,           # Colors in palette
            0            # Important colors
        )
        
        # Pixel data: 2x2 red pixels (BGR format for BMP)
        # Each row must be padded to a multiple of 4 bytes
        # Row 1: 2 pixels * 3 bytes = 6 bytes, padded to 8
        row = b'\x00\x00\xff' * 2 + b'\x00\x00'  # 2 red pixels + 2 bytes padding
        pixels = row * 2  # 2 rows
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        # Write the BMP file
        with open(path, 'wb') as f:
            f.write(file_header)
            f.write(info_header)
            f.write(pixels)
        
        print(f"  Created test image: {path}")
        return True
        
    except Exception as e:
        print(f"  Could not create test image: {e}")
        return False


# ========================================
# FIND TEST IMAGES
# ========================================

def find_test_images():
    """
    Look for existing images in the media directory,
    or create a test image if none exist.
    
    Returns a list of (image_path, description) tuples.
    """
    
    images = []
    
    # Check the standard upload directory for existing images
    media_dir = "app/media/tmp/images"
    
    if os.path.exists(media_dir):
        # Look for any image files
        for filename in os.listdir(media_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp')):
                filepath = os.path.join(media_dir, filename)
                images.append((filepath, f"Existing upload: {filename}"))
    
    # If no images found, create a simple test image
    if not images:
        test_path = os.path.join(media_dir, "test_image.bmp")
        if create_test_image(test_path):
            images.append((test_path, "Auto-generated test image (2x2 red square)"))
    
    # Also test with a non-existent file to verify error handling
    images.append(("app/media/tmp/images/does_not_exist.jpg", "Non-existent file (error handling test)"))
    
    return images


# ========================================
# MAIN TEST FUNCTION
# ========================================

async def run_tests():
    """
    Run image analysis tests and display the results.
    """
    
    print("=" * 70)
    print("🖼️  IMAGE ANALYSIS SERVICE TEST")
    print("=" * 70)
    print()
    print("Model: Salesforce/blip-image-captioning-base")
    print("First request may take 20-40 seconds (model loading)...")
    print()
    
    # Find test images
    test_images = find_test_images()
    
    print(f"Found {len(test_images)} test image(s)")
    print()
    
    # Run each test
    for i, (image_path, description) in enumerate(test_images, 1):
        print(f"--- Test {i}/{len(test_images)}: {description} ---")
        print(f"  Path: {image_path}")
        
        # Check if file exists
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            print(f"  File size: {file_size:,} bytes")
        else:
            print(f"  File: DOES NOT EXIST (testing error handling)")
        
        print(f"  Analyzing...")
        
        # Call the image analyzer
        result = await analyze_image(image_path)
        
        # Display results
        caption = result["caption"]
        method = result["method"]
        
        print(f"  Method: {method}")
        print(f"  Caption: \"{caption}\"")
        
        if method == "ml":
            print(f"  ✅ Real ML caption generated!")
        elif method == "error":
            print(f"  ℹ️  Error handled gracefully: {result.get('reason', '')}")
        elif method == "fallback":
            print(f"  ⚠️  Fallback used: {result.get('reason', '')}")
        elif method == "skipped":
            print(f"  ℹ️  Skipped: {result.get('reason', '')}")
        elif method == "passthrough":
            print(f"  ℹ️  Passthrough")
        
        print()
    
    # Summary
    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print()
    print("What to check:")
    print("  1. Real images should get ML-generated captions")
    print("  2. Missing files should be handled gracefully (no crash)")
    print("  3. The test image may get a generic caption (it's just a colored square)")
    print()
    print("For better results, upload a real photo (e.g., a photo from your phone)")
    print("to app/media/tmp/images/ and run this test again.")


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_tests())