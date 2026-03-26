# backend/scripts/test_asr.py
# Test script for ASR service
# Run this to verify Hugging Face API integration works

# Import asyncio to run async functions
import asyncio

# Import Path for file handling
from pathlib import Path

# Import the ASR service functions
from app.services.asr import transcribe_audio, check_asr_api_status


# ========================================
# MAIN TEST FUNCTION
# ========================================

async def test_asr():
    """
    Test the ASR service with real audio file.
    """
    
    print("="*60)
    print("ASR SERVICE TEST")
    print("="*60)
    print()
    
    # ========================================
    # TEST 1: Check API Status
    # ========================================
    
    print("Test 1: Checking Hugging Face API status...")
    status = await check_asr_api_status()
    print(f"API Status: {status}")
    print()
    
    
    # ========================================
    # TEST 2: Find Audio File
    # ========================================
    
    print("Test 2: Looking for audio files...")
    
    # Path to audio directory
    audio_dir = Path("backend/app/media/tmp/audio")

    
    # Check if directory exists
    if not audio_dir.exists():
        print(f"Error: Audio directory doesn't exist: {audio_dir}") 
        return
    
    # List all files in audio directory
    audio_files = list(audio_dir.glob("*.wav")) + list(audio_dir.glob("*.mp3"))
    
    # Check if any audio files found
    if not audio_files:
        print("No audio files found in app/media/tmp/audio/")
        print("Please upload an audio file via the frontend first")
        return
    
    # Use first audio file found
    test_file = str(audio_files[0])
    print(f"Found audio file: {test_file}")
    print()
    
    
    # ========================================
    # TEST 3: Transcribe Audio
    # ========================================
    
    print("Test 3: Transcribing audio...")
    print("(This may take 10-30 seconds...)")
    print()
    
    try:
        # Call transcription service
        transcript = await transcribe_audio(test_file)
        
        # Display results
        print("="*60)
        print("TRANSCRIPTION SUCCESSFUL!")
        print("="*60)
        print()
        print(f"File: {Path(test_file).name}")
        print(f"Transcript: {transcript}")
        print()
        print(f"Length: {len(transcript)} characters")
        print(f"Words: ~{len(transcript.split())} words")
        print()
        
    except Exception as e:
        # Transcription failed
        print("="*60)
        print("TRANSCRIPTION FAILED!")
        print("="*60)
        print()
        print(f"Error: {str(e)}")
        print()
        print("Possible causes:")
        print("- HUGGINGFACE_API_KEY not set in .env")
        print("- Invalid API key")
        print("- Network connection issue")
        print("- Hugging Face API temporarily unavailable")
        print()


# ========================================
# RUN TEST
# ========================================

if __name__ == "__main__":
    """
    Run this script directly to test ASR service:
    
    From backend directory:
        python -m scripts.test_asr
    """
    
    # Run the async test function
    asyncio.run(test_asr())