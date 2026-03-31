# Risk Scoring System - CivicLens Dispatch

## Overview

The risk scoring system analyzes incident text and produces a 0.0 to 1.0 urgency score. This score helps dispatchers prioritize incidents — higher scores indicate situations that need immediate attention.

## How It Works

### Model

We use `facebook/bart-large-mnli` via the Hugging Face Inference API. This is a zero-shot classification model, meaning it can classify text into categories it was never specifically trained on.

### Method: Zero-Shot Classification

Instead of training a custom model on labeled dispatch data (which we don't have), we define urgency categories and let the model determine which category best fits the incident text.

**Urgency Labels (from most to least urgent):**

1. "critical life-threatening emergency" → weight 1.0
2. "high urgency dangerous situation" → weight 0.8
3. "moderate concern requires attention" → weight 0.5
4. "low priority non-urgent matter" → weight 0.2
5. "routine informational report" → weight 0.0

### Score Calculation

The model returns a confidence score (0.0 to 1.0) for each label. These confidences always sum to 1.0.

We calculate the final risk score as a weighted sum:

```
risk_score = sum(label_confidence × label_weight)
```

**Example:**

For "Building on fire, people trapped":
- critical emergency: 0.72 × 1.0 = 0.720
- high urgency: 0.15 × 0.8 = 0.120
- moderate concern: 0.08 × 0.5 = 0.040
- low priority: 0.03 × 0.2 = 0.006
- routine: 0.02 × 0.0 = 0.000

**Final score: 0.886** (high urgency — correct!)

For "Streetlight flickering on Main Street":
- routine: 0.60 × 0.0 = 0.000
- low priority: 0.25 × 0.2 = 0.050
- moderate concern: 0.10 × 0.5 = 0.050
- high urgency: 0.03 × 0.8 = 0.024
- critical emergency: 0.02 × 1.0 = 0.020

**Final score: 0.144** (low urgency — correct!)

## Input

The risk scorer receives combined text from:
- Incident description (from the form)
- Audio transcript (if available, from Whisper ASR)

More text gives the model better context for accurate scoring.

## Fallback System

If the Hugging Face API is unavailable, the system falls back to keyword-based scoring:

- Critical keywords (fire, explosion, shooting) → +0.25
- High urgency keywords (injured, accident) → +0.20
- Moderate keywords (hazard, suspicious) → +0.10
- Low priority indicators (noise, parking) → -0.15

This ensures every incident gets a score, even during API outages.

## Error Handling

- **503 (Model Loading):** Retries up to 4 times with increasing delays
- **429 (Rate Limited):** Retries with longer delays
- **401 (Bad API Key):** Fails immediately with clear error message
- **Timeout:** Retries, then falls back to rule-based scoring
- **Any other error:** Falls back to rule-based scoring

## File Structure

```
backend/app/services/
├── risk_scorer.py          # Risk scoring service (Day 45)
├── asr.py                  # Audio transcription (Day 33)
├── incident_processor.py   # Pipeline orchestrator (calls all services)
```

## Testing

Run the test script:
```bash
cd backend
source ../.venv/bin/activate
python scripts/test_risk_scorer.py
```

This tests 6 scenarios from critical emergencies to routine reports.

## Design Decisions

**Why zero-shot classification instead of a custom model?**
- No labeled training data needed
- Works immediately with any categories
- Easy to adjust urgency labels without retraining
- Good enough for MVP (can upgrade later)

**Why BART-MNLI?**
- State-of-the-art for zero-shot classification
- Available free on Hugging Face Inference API
- Understands nuanced language well
- Fast inference time

**Why weighted scoring instead of just taking the top label?**
- Produces continuous scores (0.0-1.0) instead of discrete categories
- Captures uncertainty (e.g., 0.55 means "maybe moderate, maybe high")
- Better for sorting and prioritization in the UI

---

*Implemented Day 45 | Model: facebook/bart-large-mnli | Method: Zero-shot classification*