# Image Analysis System - CivicLens Dispatch

## Overview

The image analysis system examines uploaded incident photos and generates text descriptions (captions) of what's in the image. This gives dispatchers quick context about the visual scene without needing to open and examine every photo.

## How It Works

### Model

`Salesforce/blip-image-captioning-base` via the Hugging Face Inference API. BLIP (Bootstrapping Language-Image Pre-training) was trained on millions of image-text pairs to understand visual scenes and describe them in natural language.

### Method

Unlike text services that send JSON, the image API receives raw image bytes. The model processes the pixels and generates a text caption word by word.

Input: Raw image bytes (JPEG, PNG, etc.)
Output: Text description like "A car accident on a highway with smoke"

### Integration with Other Services

The image caption isn't just stored — it's fed into the other AI services too:

- **Classification:** "Image shows: a burning building" helps classify as fire even if the text description is vague
- **Summarization:** "Visual observation: smoke and flames" enriches the summary
- **Risk scoring:** Visual context like "people lying on ground" increases urgency score

This cross-modal integration makes each service more accurate.

## Input Handling

- Files must exist on disk (path from database)
- Maximum file size: 5 MB
- Supported formats: JPEG, PNG, GIF, BMP, WebP
- Missing or corrupt files are handled gracefully
- Very small files (<100 bytes) are treated as corrupt

## Fallback System

If the BLIP API is unavailable, the image_caption field is set to "[Image analysis unavailable]". The incident is still fully processed by all text-based services — image analysis failure doesn't block the pipeline.

## File Structure

```
backend/app/services/
├── image_analyzer.py       # Image analysis (Day 48)
├── summarizer.py           # Summarization (Day 47)
├── text_classifier.py      # Classification (Day 46)
├── risk_scorer.py          # Risk scoring (Day 45)
├── asr.py                  # Audio transcription (Day 33)
├── incident_processor.py   # Pipeline orchestrator
```

## Testing

```bash
cd backend
source ../.venv/bin/activate
python scripts/test_image_analyzer.py
```

Place a real photo in `app/media/tmp/images/` for meaningful captions. The auto-generated test image (colored square) will get a generic caption.

## Models Summary (Complete System)

| Model | Task | Modality |
|-------|------|----------|
| openai/whisper-base | Audio transcription | Audio |
| facebook/bart-large-mnli | Classification + Risk scoring | Text |
| facebook/bart-large-cnn | Summarization | Text |
| Salesforce/blip-image-captioning-base | Image captioning | Vision |

CivicLens is now truly multimodal — processing audio, text, and images!

---

*Implemented Day 48 | Model: Salesforce/blip-image-captioning-base | Multimodal pipeline complete*