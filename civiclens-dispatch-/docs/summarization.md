# Summarization System - CivicLens Dispatch

## Overview

The summarization system takes incident text (description + audio transcript) and generates a concise summary that captures the key facts. This helps dispatchers quickly understand each incident without reading the full report.

## How It Works

### Model

`facebook/bart-large-cnn` via the Hugging Face Inference API. This model was trained on CNN/DailyMail news articles and their human-written summaries. News articles are structurally similar to incident reports — both describe events with details about what happened, where, and who was involved.

### Method: Abstractive Summarization

Unlike extractive summarization (which copies sentences from the original), abstractive summarization generates new text that paraphrases the key information. This produces more natural, readable summaries.

### Parameters

- `min_length: 20` — Summary must be at least ~20 words
- `max_length: 100` — Summary should be at most ~100 words
- `do_sample: False` — Deterministic output (same input always produces same summary)

### Input Handling

- Text shorter than 80 characters is returned as-is (too short to summarize)
- Text longer than 3000 characters is truncated (model's token limit)
- Description and transcript are combined before summarizing

## Compared to the Old Template Stub

**Old approach (template):**
```
"Fire incident. Emergency fire alarm activated at... Audio transcript available. Caller reported distress."
```
Always the same structure. Doesn't capture actual details. Mentions "distress" even when there is none.

**New approach (ML):**
```
"A fire has broken out at a shopping center on Oak Boulevard, injuring three people. Multiple fire trucks are on scene as the blaze spreads to neighboring stores. Traffic has been diverted."
```
Captures the specific facts. Reads naturally. Adapts to each incident.

## Fallback System

If the BART-Large-CNN API is unavailable, the system falls back to simple text truncation: takes the first 150 characters of the input and adds ellipsis. Not ideal, but ensures every incident gets some form of summary.

## Error Handling

Same retry pattern as other services:
- 503: Retry up to 5 times (this model is larger, may need more loading time)
- 429: Retry with longer delays
- 401: Fail immediately
- Timeout: 90 seconds per request (summarization generates text, which takes longer)

## This vs Classification/Risk Scoring

| Feature | Classification | Risk Scoring | Summarization |
|---------|---------------|-------------|---------------|
| Model | bart-large-mnli | bart-large-mnli | bart-large-cnn |
| Task | Categorize text | Score urgency | Generate summary |
| Output | Label (fire, medical) | Number (0.0-1.0) | Generated text |
| API calls | 2 per incident | 1 per incident | 1 per incident |

## File Structure

```
backend/app/services/
├── summarizer.py           # Summarization (Day 47) — LAST STUB REPLACED!
├── text_classifier.py      # Classification (Day 46)
├── risk_scorer.py          # Risk scoring (Day 45)
├── asr.py                  # Audio transcription (Day 33)
├── incident_processor.py   # Pipeline orchestrator
```

## Testing

```bash
cd backend
source ../.venv/bin/activate
python scripts/test_summarizer.py
```

Tests 5 scenarios: long fire report, highway accident, short noise complaint, infrastructure issue, and a crime report with transcript.

## Design Decisions

**Why a different model than classification?**
BART-MNLI is trained for understanding/classifying text. BART-Large-CNN is trained for generating text. Summarization requires text generation, so we need the CNN-trained variant.

**Why min_length=20 and max_length=100?**
Dispatcher summaries should be quick to scan — long enough to capture key facts, short enough to read at a glance. 20-100 words hits that sweet spot.

**Why do_sample=False?**
Deterministic output means the same incident always gets the same summary. This is important for consistency — if a dispatcher reads a summary, refreshes the page, and sees a different summary, that would be confusing.

**Why passthrough for short text?**
If the original text is already short (like "Noise complaint from apartment 4B"), running it through a summarization model would produce output that's the same length or longer. Just return the original.

---

*Implemented Day 47 | Model: facebook/bart-large-cnn | The LAST stub replaced!*