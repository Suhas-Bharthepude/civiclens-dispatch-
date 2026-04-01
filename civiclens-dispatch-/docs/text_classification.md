# Text Classification System - CivicLens Dispatch

## Overview

The text classification system analyzes incident text and determines two things: the incident type (fire, medical, traffic, etc.) and the severity level (high, medium, low). This helps dispatchers route incidents to the right department and understand the scale of response needed.

## How It Works

### Model

Same as risk scoring: `facebook/bart-large-mnli` via the Hugging Face Inference API. Zero-shot classification — no custom training data needed.

### Method: Two-Pass Classification

We make two separate API calls per incident:

**Pass 1 — Incident Type:**
The model chooses from 7 type labels:
- "fire or explosion emergency" → fire
- "medical emergency or health crisis" → medical
- "traffic accident or vehicle collision" → traffic
- "criminal activity theft robbery or assault" → crime
- "noise disturbance or noise complaint" → noise
- "infrastructure damage water leak or flood" → infrastructure
- "other general matter or miscellaneous issue" → other

**Pass 2 — Severity:**
The model chooses from 3 severity labels:
- "critical high severity life-threatening emergency" → high
- "moderate severity situation requiring attention" → medium
- "minor low severity non-urgent issue" → low

### Why Two Passes?

Zero-shot classification requires all candidate labels in a single request. Since type labels and severity labels are different dimensions, we run two separate requests. You can't ask the model to pick from "fire" AND "high severity" in the same call — it would treat them as competing alternatives.

## Input

The classifier receives combined text from the incident description and audio transcript (if available). More text gives the model better context.

## Compared to the Old Keyword Stub

**Old approach (keyword matching):**
- "fire" in text → type=fire, severity=high
- Problem: "Small grease fire, already extinguished" gets severity=high (wrong!)
- Problem: Can't handle text without exact keywords

**New approach (ML zero-shot):**
- Model understands the MEANING of the text, not just keyword presence
- "Small grease fire, already extinguished" → type=fire, severity=low (correct!)
- "Several people are reporting feeling unwell after a gas leak" → type=medical (no keyword "injured" needed)

## Fallback System

If the Hugging Face API is unavailable, the system falls back to the original keyword-based classification. This ensures every incident gets classified even during API outages.

## Error Handling

Same patterns as risk scoring (Day 45):
- 503: Retry up to 4 times
- 429: Retry with longer delays
- 401: Fail immediately
- Timeout: Retry, then fallback

## File Structure

```
backend/app/services/
├── text_classifier.py      # Text classification (Day 46)
├── risk_scorer.py          # Risk scoring (Day 45)
├── asr.py                  # Audio transcription (Day 33)
├── incident_processor.py   # Pipeline orchestrator
```

## Testing

```bash
cd backend
source ../.venv/bin/activate
python scripts/test_classifier.py
```

Tests 8 scenarios covering all incident types and severity levels.

## Design Decisions

**Why two API calls instead of one combined call?**
Type and severity are different dimensions. Combining them into one label set (like "high-severity fire") would create a combinatorial explosion (7 types × 3 severities = 21 labels), reducing classification accuracy.

**Why the same model as risk scoring?**
BART-MNLI is already loaded in memory on Hugging Face from our risk scoring calls. Reusing it means no additional model loading time. The same model handles both tasks well.

**Why natural language labels instead of short labels?**
The model was trained on natural language inference. "fire or explosion emergency" gives the model much more semantic context than just "fire," leading to more accurate classification.

---

*Implemented Day 46 | Model: facebook/bart-large-mnli | Method: Two-pass zero-shot classification*