# Pipeline Optimization - CivicLens Dispatch

## Overview

Day 49 restructured the AI processing pipeline from sequential execution to parallel execution, reducing total processing time significantly.

## Before vs After

### Sequential (Days 34-48)

```
ASR (10s) → Image (5s) → Classification (8s) → Summarization (6s) → Risk (4s)
Total: 33 seconds (sum of all steps)
```

Each step waited for the previous one to finish, even when they didn't depend on each other.

### Parallel (Day 49+)

```
Phase 1 (parallel):
  ASR (10s) ─────┐
  Image (5s) ────┤  ← Both run simultaneously
                  ↓
Phase 1 total: 10s (slowest task only)

Phase 2 (parallel):
  Classification (8s) ───┐
  Summarization (6s) ────┤  ← All three run simultaneously
  Risk scoring (4s) ─────┘
                          ↓
Phase 2 total: 8s (slowest task only)

Total: ~18 seconds (nearly half the sequential time)
```

## Why Two Phases?

Phase 2 tasks (classification, summarization, risk scoring) all analyze TEXT. If an audio file was uploaded, that text includes the transcript from Phase 1's ASR. So Phase 2 must wait for Phase 1 to finish — it needs the transcript.

Within each phase, tasks are truly independent and can safely run simultaneously.

## How It Works: asyncio.gather()

```python
# Run tasks A, B, C at the same time
results = await asyncio.gather(task_a(), task_b(), task_c())
# results[0] = task_a's result
# results[1] = task_b's result  
# results[2] = task_c's result
# Total time = max(time_a, time_b, time_c), NOT sum
```

## Error Handling

Each task is wrapped in `_timed_task()` which catches exceptions individually. If ASR fails, image analysis still completes. If summarization fails, classification and risk scoring still complete. No single failure kills the entire pipeline.

## Timing Measurements

Every step is timed with `time.perf_counter()` (Python's most precise timer). The pipeline logs show:
- Individual task times
- Phase totals
- Overall pipeline duration

This data helps identify bottlenecks for future optimization.

## Performance Results

Typical times on Hugging Face free tier:

| Step | Sequential | Parallel |
|------|-----------|----------|
| ASR | 5-30s | Phase 1: max(ASR, Image) |
| Image | 3-10s | = 5-30s |
| Classification | 5-15s | Phase 2: max(Class, Sum, Risk) |
| Summarization | 5-15s | = 5-15s |
| Risk scoring | 3-10s | |
| **Total** | **21-80s** | **10-45s** |

Improvement: 40-50% reduction in total processing time.

## Future Optimizations

- Connection pooling for HTTP clients (reuse connections)
- Model caching (keep models warm with periodic pings)
- Batch processing (process multiple incidents at once)
- Celery + Redis for distributed task queues

---

*Implemented Day 49 | Method: asyncio.gather() parallel execution*