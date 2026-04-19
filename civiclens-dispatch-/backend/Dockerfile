# backend/Dockerfile
#
# Recipe for building the CivicLens Dispatch backend into a Docker image.
# Docker reads this top to bottom and executes each instruction in order.
#
# Build manually:  docker build -t civiclens-backend .
# Run via compose: docker compose up --build
#
# Day 68: Docker containerization

# ============================================================
# BASE IMAGE
# Start from an official Python 3.11 image on slim Linux.
# "slim" = minimal OS with just enough to run Python (~50MB vs 900MB full).
# We pin to 3.11 specifically so the image never changes unexpectedly.
# ============================================================

FROM python:3.11-slim


# ============================================================
# SYSTEM DEPENDENCIES
# Install Linux packages that some Python packages need to compile.
# This runs before everything else because it rarely changes
# and we want Docker to cache it aggressively.
# ============================================================

RUN apt-get update \
    # --no-install-recommends keeps the image small (no optional extras)
    && apt-get install -y --no-install-recommends \
        # curl is needed for the health check command later
        curl \
        # gcc is a C compiler needed by some Python packages
        gcc \
        # libpq-dev has PostgreSQL client headers (needed when we add Postgres)
        libpq-dev \
    # Delete the package cache after install — we don't need it anymore
    # This reduces the final image size
    && rm -rf /var/lib/apt/lists/*


# ============================================================
# WORKING DIRECTORY
# All subsequent instructions run inside /app.
# This is the folder where your code lives inside the container.
# ============================================================

# Create /app and switch into it
WORKDIR /app


# ============================================================
# INSTALL PYTHON DEPENDENCIES
# IMPORTANT: We copy requirements.txt and install packages BEFORE
# copying the rest of the code.
#
# Why? Docker caches each step as a "layer."
# If requirements.txt hasn't changed, Docker reuses the cached
# pip install layer even if your Python files changed.
# This makes rebuilds much faster — seconds instead of minutes.
# ============================================================

# Copy only requirements.txt first (not the whole project)
COPY requirements.txt .

# Upgrade pip then install everything in requirements.txt
# --no-cache-dir = don't store pip's download cache (reduces image size)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt


# ============================================================
# COPY APPLICATION CODE
# Now copy the rest of the code — AFTER pip install.
# The .dockerignore file controls what gets excluded:
#   .venv, .env, .git, __pycache__, test.db are all excluded.
# ============================================================

# Copy everything from backend/ into /app inside the container
COPY . .


# ============================================================
# CREATE UPLOAD DIRECTORIES
# The app saves uploaded audio and images here.
# These directories must exist before uvicorn starts.
# ============================================================

# -p = create parent directories too, no error if they already exist
RUN mkdir -p app/media/tmp/audio \
    && mkdir -p app/media/tmp/images \
    && mkdir -p app/media/tmp/documents


# ============================================================
# ENVIRONMENT VARIABLES
# Default env vars that apply inside the container.
# These can all be overridden by docker-compose.yml or the hosting platform.
# ============================================================

# Don't write .pyc bytecode files — not needed in a container
ENV PYTHONDONTWRITEBYTECODE=1

# Don't buffer stdout/stderr — print() output appears in docker logs immediately
ENV PYTHONUNBUFFERED=1

# Set Python module search path to /app so imports work correctly
ENV PYTHONPATH=.


# ============================================================
# EXPOSE PORT
# Documents that the container listens on port 8000.
# This alone doesn't publish the port — docker-compose.yml does that.
# ============================================================

EXPOSE 8000


# ============================================================
# STARTUP COMMAND
# The command Docker runs when the container starts.
# --host 0.0.0.0 = accept connections from any IP (required in Docker)
# --port 8000    = listen on port 8000
# --workers 1    = one worker (fine for dev; increase for production)
# No --reload    = auto-reload is for development only, not containers
# ============================================================

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]