# ASR Testing Guide (Day 33)

## Testing the ASR Service

### Quick Test
```bash
cd backend
source ../.venv/bin/activate
python -m scripts.test_asr
```

### Test Script Features

**What it tests:**
1. API connectivity (checks if HF API is reachable)
2. API authentication (validates API key works)
3. File reading (ensures audio file exists and is readable)
4. Transcription (actual ASR call)
5. Error handling (retries, timeouts)

### Expected Results

**Successful test:**
```
============================================================
TRANSCRIPTION SUCCESSFUL!
============================================================

File: recording.wav
Transcript: There is a fire emergency at 123 Main Street.

Length: 52 characters
Words: ~9 words
```

**Model loading (first request):**
```
[ASR] Response status: 503
[ASR] Model is loading, will retry...
[ASR] Waiting 2 seconds before retry...
[ASR] Attempt 2/3
[ASR] Response status: 200
[ASR] Transcription successful: ...
```

This is normal! First request loads model into memory (takes ~20 seconds).

### Troubleshooting

**Error: "Audio file not found"**
- **Cause:** No audio files in media/tmp/audio/
- **Fix:** Upload audio via frontend first

**Error: "Invalid Hugging Face API key"**
- **Cause:** HUGGINGFACE_API_KEY not in .env or incorrect
- **Fix:** Check .env file, verify token starts with `hf_`

**Error: "Model still loading after all retries"**
- **Cause:** Model taking very long to load (rare)
- **Fix:** Wait 30 seconds and run test again

**Error: "Rate limit exceeded"**
- **Cause:** Too many requests in short time (30/minute limit)
- **Fix:** Wait 1 minute and try again

**Error: "Request timed out"**
- **Cause:** Network slow or API unresponsive
- **Fix:** Check internet connection, retry

### Manual Testing with Python
```python
# In Python REPL
python

>>> import asyncio
>>> from app.services.asr import transcribe_audio
>>> 
>>> # Test transcription
>>> result = asyncio.run(transcribe_audio("app/media/tmp/audio/test.wav"))
>>> print(result)
```

### Testing Accuracy

**Create test set:**
1. Record clear audio: "This is a test"
2. Record noisy audio: (with background noise)
3. Record fast speech
4. Record with accent

**Compare results:**
- Clear audio should be 95%+ accurate
- Noisy audio should be 80-90% accurate
- Fast speech should be 85-90% accurate

### Performance Benchmarks

**Typical processing times:**
- 10 second audio: ~5 seconds
- 30 second audio: ~10 seconds
- 1 minute audio: ~15 seconds
- 5 minute audio: ~30 seconds

**First request:** Add 15-20 seconds (model loading)

**Rate limits:**
- Free tier: 30 requests/minute
- If hit limit: Wait 60 seconds

---

*ASR testing guide: Day 33*