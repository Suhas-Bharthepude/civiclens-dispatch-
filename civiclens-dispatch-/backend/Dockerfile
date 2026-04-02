# backend/Dockerfile
# Builds a Docker container for the CivicLens Dispatch FastAPI backend
#
# This container includes:
#   - Python 3.13
#   - All Python dependencies from requirements.txt
#   - The application code
#   - Uvicorn server configured to start automatically
#
# Usage:
#   docker build -t civiclens-backend .
#   docker run -p 8000:8000 --env-file .env civiclens-backend
#
# Or use docker-compose (recommended):
#   docker-compose up --build
#
# Day 58: Docker containerization

# ========================================
# BASE IMAGE
# ========================================
# Start from the official Python 3.13 slim image
# "slim" is a smaller version (~150MB vs ~1GB for full)
# It has Python pre-installed but not extra tools we don't need
FROM python:3.13-slim

# ========================================
# ENVIRONMENT VARIABLES
# ========================================
# PYTHONDONTWRITEBYTECODE=1 prevents Python from creating .pyc files
# These cache files are unnecessary in a container (saves space)
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED=1 forces Python to print output immediately
# Without this, log messages might be delayed or lost in Docker
ENV PYTHONUNBUFFERED=1

# ========================================
# WORKING DIRECTORY
# ========================================
# Set the working directory inside the container
# All subsequent commands run from this directory
# This is like doing "cd /app" inside the container
WORKDIR /app

# ========================================
# INSTALL DEPENDENCIES
# ========================================
# Copy requirements.txt FIRST, before the rest of the code
# This is a Docker optimization called "layer caching"
# If requirements.txt hasn't changed, Docker reuses the cached layer
# and skips pip install (which is slow), even if your code changed
COPY requirements.txt .

# Install all Python packages from requirements.txt
# --no-cache-dir saves space by not caching downloaded packages
# --upgrade pip ensures we have the latest pip version
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ========================================
# COPY APPLICATION CODE
# ========================================
# Copy the entire backend directory into the container
# The .dockerignore file excludes unnecessary files (.venv, test.db, etc.)
COPY . .

# ========================================
# CREATE MEDIA DIRECTORIES
# ========================================
# Ensure the upload directories exist inside the container
# These are where audio and image files get stored temporarily
RUN mkdir -p app/media/tmp/audio app/media/tmp/images

# ========================================
# EXPOSE PORT
# ========================================
# Document that this container listens on port 8000
# This doesn't actually publish the port — that's done with -p flag or docker-compose
EXPOSE 8000

# ========================================
# STARTUP COMMAND
# ========================================
# The command that runs when the container starts
# uvicorn app.main:app — runs the FastAPI application
# --host 0.0.0.0 — listen on all network interfaces (required for Docker)
#   Without this, the server only listens on localhost (127.0.0.1)
#   which is not accessible from outside the container
# --port 8000 — listen on port 8000
# --workers 2 — run 2 worker processes for handling concurrent requests
#   In production, set this to (2 * CPU_CORES) + 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]