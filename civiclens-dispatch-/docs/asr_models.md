# ASR (Automatic Speech Recognition) Models (Day 32)

## What is ASR?

**ASR** = Automatic Speech Recognition = Speech-to-Text

Converts spoken words in audio recordings into written text.

## How ASR Works (Simplified)

### Traditional Approach (Pre-2020)
```
Audio → Feature Extraction → Acoustic Model → Language Model → Text
         (spectrograms)      (phonemes)        (words)
```

**Complex:** Multiple stages, each needs tuning

### Modern Approach (Deep Learning)
```
Audio → Neural Network → Text
        (end-to-end)
```

**Simple:** One model does everything

## Whisper by OpenAI

### Overview

- **Developer:** OpenAI
- **Release:** September 2022
- **Training:** 680,000 hours of multilingual audio
- **Languages:** 99 languages
- **License:** MIT (open source, free to use)

### Why Whisper?

✅ **Robust to noise** - Handles background sounds, poor quality audio  
✅ **Multilingual** - Works with accents and code-switching  
✅ **Punctuation** - Adds punctuation automatically  
✅ **Timestamps** - Can provide word-level timing  
✅ **Open source** - Free, can run locally or via API  
✅ **Well-documented** - Lots of examples and guides  

### Whisper Model Sizes

| Model | Parameters | Size | Speed | Use Case |
|-------|-----------|------|-------|----------|
| tiny | 39M | 39MB | ~32x realtime | Real-time apps, low-power devices |
| base | 74M | 142MB | ~16x realtime | **Recommended for CivicLens** |
| small | 244M | 466MB | ~6x realtime | Better accuracy needed |
| medium | 769M | 1.5GB | ~2x realtime | High accuracy |
| large | 1550M | 2.9GB | ~1x realtime | Maximum accuracy |

**Realtime speed:**
- 32x = processes 32 seconds of audio in 1 second
- 1x = processes 1 second of audio in 1 second

**For CivicLens:** **base** or **small** model

- Emergency calls are usually < 5 minutes
- base model processes 5 min audio in ~20 seconds
- Good balance of speed and accuracy

## Hugging Face Inference API

### What is Hugging Face?

- Platform for sharing AI models
- Like GitHub for machine learning
- 100,000+ models available
- Free hosting and inference API

### Inference API Benefits

**Without Inference API:**
```python
# Download 142MB model
# Install dependencies (PyTorch, transformers)
# Load model into memory (uses 500MB RAM)
# Write inference code
# Manage GPU/CPU
```

**With Inference API:**
```python
# Just call API endpoint
response = requests.post(url, data=audio_bytes)
transcript = response.json()["text"]
```

**Comparison:**

| Aspect | Local Model | Inference API |
|--------|-------------|---------------|
| Setup | Complex | Simple |
| Hardware | GPU recommended | None needed |
| Speed | Fast (local) | Medium (network) |
| Cost | $0 (once set up) | Free tier + paid |
| Scaling | Manual | Automatic |

### Free Tier Limits

**Hugging Face Free Tier:**
- ✅ Unlimited model calls per day
- ⚠️ Rate limited (30 requests/minute)
- ⚠️ May queue if server busy
- ✅ All models available

**Good enough for:**
- Development and testing ✅
- Low-volume production (< 1000 calls/day) ✅
- Proof of concept ✅

**Not good for:**
- High-volume production (10,000+ calls/day)
- Real-time requirements (< 1 second latency)
- Strict privacy requirements (data sent to HF servers)

**Solution for high volume:** Run Whisper locally (Day 51+)

## Alternative ASR Options

### Google Cloud Speech-to-Text

**Pros:**
- Excellent accuracy
- Low latency
- Real-time streaming

**Cons:**
- Costs money ($0.006 per 15 seconds)
- Requires Google Cloud account
- Complex setup

### Amazon Transcribe

**Pros:**
- Good accuracy
- AWS integration
- Scalable

**Cons:**
- Costs money
- Requires AWS account
- Complex pricing

### AssemblyAI

**Pros:**
- Simple API
- Good accuracy
- Affordable

**Cons:**
- Costs money ($0.00025 per second)
- Not open source

### Local Whisper (Self-Hosted)

**Pros:**
- Free (after setup)
- Fast (local processing)
- Private (data stays on your server)
- No rate limits

**Cons:**
- Requires GPU (or very slow on CPU)
- Complex setup
- Need to manage infrastructure

**For CivicLens:**
- **Now (Days 32-35):** Hugging Face API (free, simple)
- **Later (Day 51+):** Option to run locally

## How to Use Whisper

### Via Hugging Face API (Our Approach)
```python
import requests

# API endpoint
API_URL = "https://api-inference.huggingface.co/models/openai/whisper-base"

# Your API token
headers = {"Authorization": "Bearer hf_xxxxx"}

# Read audio file
with open("audio.wav", "rb") as f:
    audio_bytes = f.read()

# Make request
response = requests.post(API_URL, headers=headers, data=audio_bytes)

# Get transcript
result = response.json()
transcript = result["text"]

print(transcript)  # "There's a fire at 123 Main Street"
```

### Via Local Installation (Future)
```python
import whisper

# Load model (first time downloads 142MB)
model = whisper.load_model("base")

# Transcribe audio
result = model.transcribe("audio.mp3")

# Get transcript
transcript = result["text"]

print(transcript)
```

## Audio Preprocessing

### What is Audio Preprocessing?

**Preparing audio for better transcription:**

**Common preprocessing:**
1. **Convert format** - MP3 → WAV (Whisper prefers WAV)
2. **Resample** - Change sample rate to 16kHz (Whisper's native rate)
3. **Normalize volume** - Ensure consistent loudness
4. **Remove silence** - Trim quiet sections at start/end
5. **Reduce noise** - Filter out background noise (optional)

**Python libraries:**
- `ffmpeg` - Format conversion
- `pydub` - Audio manipulation
- `librosa` - Audio analysis
- `noisereduce` - Noise reduction

**Example:**
```python
from pydub import AudioSegment

# Load MP3
audio = AudioSegment.from_mp3("input.mp3")

# Convert to WAV, 16kHz mono
audio = audio.set_frame_rate(16000).set_channels(1)

# Export
audio.export("output.wav", format="wav")
```

## Transcription Quality

### Factors Affecting Accuracy

**Audio Quality (Most Important):**
- Clear recording: 95%+ accuracy
- Phone quality: 85-92% accuracy
- Poor quality: 70-85% accuracy

**Speaker Factors:**
- Clear speech: 95%+ accuracy
- Fast speech: 85-90% accuracy
- Heavy accent: 85-95% accuracy (Whisper good with accents)
- Multiple speakers: 80-90% accuracy

**Content Factors:**
- Common words: 95%+ accuracy
- Technical terms: 85-90% accuracy
- Proper nouns (names): 70-85% accuracy
- Numbers/addresses: 75-85% accuracy

**Environmental Factors:**
- Quiet environment: 95%+ accuracy
- Background noise: 85-90% accuracy
- Very noisy (sirens, traffic): 70-85% accuracy

### Emergency Call Challenges

**Common issues with 911 calls:**
- Caller under stress (fast, unclear speech)
- Background noise (sirens, crying, traffic)
- Poor phone connection
- Multiple speakers (caller + others in background)
- Shouting or emotional speech

**Whisper is good at:**
- ✅ Handling noise
- ✅ Understanding stressed speech
- ✅ Multiple accents
- ✅ Poor audio quality

**Still struggles with:**
- ❌ Extremely loud background noise
- ❌ Very heavy accents
- ❌ Made-up words or gibberish
- ❌ Very long silences

## Integration Strategy

### Phase 1: Hugging Face API (Days 33-35)

**Setup:**
1. Get API token
2. Store in .env
3. Call API from backend
4. Return transcript to frontend

**Code location:**
- `backend/app/services/asr.py` - ASR service
- Calls Hugging Face API
- Returns transcript text

**Pros:**
- ✅ Quick to implement
- ✅ No infrastructure needed
- ✅ Good for MVP

**Cons:**
- ⚠️ Rate limited
- ⚠️ Network dependency

### Phase 2: Local Whisper (Day 51+ - Optional)

**Setup:**
1. Install PyTorch
2. Install Whisper
3. Download model
4. Run on GPU

**Code:**
- Same `asr.py` interface
- Switch backend implementation
- Frontend unchanged

**Pros:**
- ✅ Faster (no network)
- ✅ No rate limits
- ✅ Private (data stays local)

**Cons:**
- ❌ Requires GPU
- ❌ Complex setup
- ❌ Infrastructure cost

## Testing Strategy

### Test Audio Files

Create test suite with:
- Clear audio (baseline)
- Noisy audio (realistic)
- Multiple speakers
- Different accents
- Technical content

### Accuracy Measurement

**Word Error Rate (WER):**
```
WER = (Substitutions + Deletions + Insertions) / Total Words

Example:
Ground truth: "There is a fire"
Transcription: "There was a fire"
WER = 1/4 = 25% error (pretty bad!)

Good WER: < 10%
Acceptable WER: 10-20%
Poor WER: > 20%
```

**For emergency calls:**
- WER < 15% is acceptable
- Key info (location, emergency type) must be correct
- Minor errors okay ("uh", "um", fillers)

## Cost Estimation

### Hugging Face Free Tier

**Limits:**
- Requests: Unlimited
- Rate: 30/minute (1 every 2 seconds)
- Queue: May wait if busy

**Suitable for:**
- 100 calls/day: ✅ Perfect
- 1,000 calls/day: ✅ Works (with queuing)
- 10,000 calls/day: ❌ Too slow

### Hugging Face Pro ($9/month)

**Benefits:**
- Higher rate limits
- Priority processing
- Faster inference

### Running Locally (GPU)

**One-time costs:**
- GPU: $200-500 (or cloud GPU: $0.50/hour)

**Ongoing:**
- Electricity: ~$5-20/month
- Or cloud GPU: $100-300/month

**Break-even:**
- Local cheaper if > 1000 transcriptions/day
- API cheaper for low volume

## Next Steps (Days 33-35)

### Day 33: Build ASR Service Function
- Create `backend/app/services/asr.py`
- Implement `transcribe_audio(file_path)` function
- Call Hugging Face API
- Handle errors and retries

### Day 34: Connect ASR to Incident Creation
- Modify background processor
- Automatically transcribe when audio uploaded
- Store transcript in database

### Day 35: Display Transcripts in UI
- Show transcript in IncidentDetail panel
- Add transcript field to table (optional)
- Highlight AI-generated content

---

*ASR research complete: Day 32*