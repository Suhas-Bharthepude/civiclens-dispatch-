# CivicLens Dispatch
Multimodal emergency triage platform using Hugging Face ASR, vision, and NLP models.

## Problem
Dispatchers manually screen unstructured 911 calls/texts/photos.

## Solution
AI pipeline: audio → transcript → classification → scoring → structured ticket.

## Tech Stack
- Backend: FastAPI + PostgreSQL + Hugging Face models
- Frontend: React + TypeScript
- Async: Celery + Redis
- Storage: MinIO/S3

## Users
1. Citizens: Submit incidents (text/audio/image)
2. Dispatchers: Triage queue with AI recommendations
