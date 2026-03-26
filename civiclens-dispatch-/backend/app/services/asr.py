# backend/app/services/asr.py
# ASR (Automatic Speech Recognition) service
# Transcribes audio files using Whisper model via Hugging Face Inference API
# Day 33: Initial implementation with Hugging Face API
# Note: Currently using mock due to HF API instability - will fix in Day 51

# Import asyncio for delays between retries
import asyncio

# Import httpx for making async HTTP requests
# httpx is like requests but supports async/await
import httpx

# Import Path for file path handling
from pathlib import Path

# Import settings to get API key from environment variables
from app.config import settings


# ========================================
# CONFIGURATION
# ========================================

# Hugging Face API endpoint for Whisper model
# Using whisper-small as it's more stable than whisper-base
HF_API_URL = "https://api-inference.huggingface.co/models/openai/whisper-small"

# Maximum number of retry attempts if API fails
# API can fail due to: model loading, rate limits, network issues
MAX_RETRIES = 3

# Delay between retries (in seconds)
# Start with 2 seconds, increase exponentially
RETRY_DELAY = 2

# Flag to use mock transcription (temporary workaround for API issues)
# Set to True to use mock, False to use real API
USE_MOCK_TRANSCRIPTION = True


# ========================================
# MAIN TRANSCRIPTION FUNCTION
# ========================================

async def transcribe_audio(audio_path: str) -> str:
    """
    Transcribe audio file using Whisper model via Hugging Face API.
    
    This function:
    1. Reads the audio file as binary data
    2. Sends it to Hugging Face Whisper API
    3. Receives transcription text
    4. Returns the transcript
    
    Args:
        audio_path: Path to audio file on disk (string)
                   Example: "backend/app/media/tmp/audio/abc-123.wav"
    
    Returns:
        Transcription text (string)
        Example: "There's a fire at 123 Main Street"
    
    Raises:
        FileNotFoundError: If audio file doesn't exist
        Exception: If API call fails after all retries
    
    Example usage:
        transcript = await transcribe_audio("audio.wav")
        print(transcript)  # "Hello world"
    """
    
    # TEMPORARY: Use mock transcription if flag is set
    # This is a workaround for Hugging Face API instability
    # Will switch to real API in Day 51 when doing production integration
    if USE_MOCK_TRANSCRIPTION:
        print("[ASR] Using mock transcription (USE_MOCK_TRANSCRIPTION=True)")
        return await transcribe_audio_mock(audio_path)
    
    # Log start of transcription
    print(f"[ASR] Starting transcription of: {audio_path}")
    
    # ========================================
    # STEP 1: Validate file exists
    # ========================================
    
    # Convert string path to Path object for easier manipulation
    # Path object has useful methods like .exists(), .stat(), etc.
    file_path = Path(audio_path)
    
    # Check if file exists on disk
    if not file_path.exists():
        # File doesn't exist - raise error
        error_msg = f"Audio file not found: {audio_path}"
        print(f"[ASR] Error: {error_msg}")
        raise FileNotFoundError(error_msg)
    
    # Log file info
    # file_path.stat().st_size gets file size in bytes
    file_size_kb = file_path.stat().st_size / 1024
    print(f"[ASR] File size: {file_size_kb:.1f} KB")
    
    
    # ========================================
    # STEP 2: Read audio file as binary data
    # ========================================
    
    # Read file in binary mode ("rb" = read binary)
    # Audio files are binary data, not text
    with open(audio_path, "rb") as audio_file:
        # Read entire file into memory as bytes
        audio_bytes = audio_file.read()
    
    # Log bytes read
    print(f"[ASR] Read {len(audio_bytes)} bytes from file")
    
    
    # ========================================
    # STEP 3: Prepare API request
    # ========================================
    
    # Prepare authorization header with API token
    # "Bearer" is the authentication scheme
    # settings.HUGGINGFACE_API_KEY comes from .env file
    headers = {
        "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
    }
    
    # Check if API key is configured
    if not settings.HUGGINGFACE_API_KEY:
        error_msg = "HUGGINGFACE_API_KEY not configured in .env file"
        print(f"[ASR] Error: {error_msg}")
        raise ValueError(error_msg)
    
    
    # ========================================
    # STEP 4: Call Hugging Face API with retries
    # ========================================
    
    # Try multiple times in case of temporary failures
    # API can fail due to: model loading, rate limits, network issues
    for attempt in range(MAX_RETRIES):
        try:
            # Log attempt number
            print(f"[ASR] Attempt {attempt + 1}/{MAX_RETRIES}")
            
            # Create async HTTP client
            # async with ensures proper cleanup (closes connection)
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Make POST request to Hugging Face API
                # Send audio bytes as request body
                # timeout=60.0 means wait up to 60 seconds for response
                response = await client.post(
                    HF_API_URL,
                    headers=headers,
                    content=audio_bytes  # Send raw audio bytes
                )
                
                # Log response status code
                print(f"[ASR] Response status: {response.status_code}")
                
                # ========================================
                # Handle different response status codes
                # ========================================
                
                # 200 = Success
                if response.status_code == 200:
                    # Parse JSON response
                    result = response.json()
                    
                    # Extract transcript text from response
                    # Hugging Face returns: {"text": "transcript here"}
                    transcript = result.get("text", "")
                    
                    # Log successful transcription
                    print(f"[ASR] Transcription successful: {transcript[:100]}...")
                    
                    # Return the transcript
                    return transcript
                
                # 503 = Model is loading (first request to model)
                elif response.status_code == 503:
                    # Model is loading - this is temporary
                    print("[ASR] Model is loading, will retry...")
                    
                    # If not last attempt, wait and retry
                    if attempt < MAX_RETRIES - 1:
                        # Wait before retrying
                        # Exponential backoff: 2s, 4s, 8s
                        delay = RETRY_DELAY * (2 ** attempt)
                        print(f"[ASR] Waiting {delay} seconds before retry...")
                        await asyncio.sleep(delay)
                        continue  # Try again
                    else:
                        # Last attempt failed
                        raise Exception("Model still loading after all retries")
                
                # 401 = Unauthorized (bad API key)
                elif response.status_code == 401:
                    error_msg = "Invalid Hugging Face API key"
                    print(f"[ASR] Error: {error_msg}")
                    raise Exception(error_msg)
                
                # 429 = Rate limit exceeded
                elif response.status_code == 429:
                    print("[ASR] Rate limit hit, will retry...")
                    
                    # Wait longer for rate limits
                    if attempt < MAX_RETRIES - 1:
                        delay = RETRY_DELAY * 3  # Wait 6 seconds
                        print(f"[ASR] Waiting {delay} seconds...")
                        await asyncio.sleep(delay)
                        continue
                    else:
                        raise Exception("Rate limit exceeded after all retries")
                
                # Other errors
                else:
                    # Unknown error status code
                    error_text = response.text
                    error_msg = f"API returned status {response.status_code}: {error_text}"
                    print(f"[ASR] Error: {error_msg}")
                    raise Exception(error_msg)
        
        except httpx.TimeoutException:
            # Request timed out (took > 60 seconds)
            print(f"[ASR] Request timed out on attempt {attempt + 1}")
            
            # If not last attempt, retry
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY
                print(f"[ASR] Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                continue
            else:
                raise Exception("Transcription timed out after all retries")
        
        except Exception as e:
            # Catch any other errors
            print(f"[ASR] Error on attempt {attempt + 1}: {str(e)}")
            
            # If last attempt, re-raise error
            if attempt == MAX_RETRIES - 1:
                raise
            
            # Otherwise wait and retry
            delay = RETRY_DELAY
            await asyncio.sleep(delay)
    
    # If we get here, all retries failed
    raise Exception("Transcription failed after all retries")


# ========================================
# HELPER FUNCTION - Mock Transcription (for testing)
# ========================================

async def transcribe_audio_mock(audio_path: str) -> str:
    """
    Mock transcription function for testing without API calls.
    
    Returns a fake transcript based on filename.
    Useful for testing the pipeline without using API quota.
    
    Args:
        audio_path: Path to audio file
    
    Returns:
        Mock transcript text
    """
    
    # Extract filename from path
    filename = Path(audio_path).name
    
    # Log mock transcription
    print(f"[ASR MOCK] Generating mock transcript for: {filename}")
    
    # Simulate processing delay (like real API would take)
    await asyncio.sleep(1)
    
    # Return fake but realistic transcript
    # This mimics what a real emergency call might sound like
    return (
        f"Caller reports a vehicle accident with possible injuries "
        f"at a downtown intersection. Caller sounds distressed. "
        f"Multiple vehicles involved. Emergency services requested."
    )


# ========================================
# UTILITY FUNCTION - Check API Status
# ========================================

async def check_asr_api_status() -> dict:
    """
    Check if Hugging Face ASR API is available.
    
    Useful for health checks and debugging.
    
    Returns:
        Dictionary with status information
    """
    
    try:
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"
        }
        
        # Make HEAD request (doesn't send data, just checks if endpoint exists)
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.head(HF_API_URL, headers=headers)
        
        # Return status info
        return {
            "available": response.status_code in [200, 503],  # 503 = model loading
            "status_code": response.status_code,
            "model": "openai/whisper-small"
        }
        
    except Exception as e:
        # API check failed
        return {
            "available": False,
            "error": str(e),
            "model": "openai/whisper-small"
        }