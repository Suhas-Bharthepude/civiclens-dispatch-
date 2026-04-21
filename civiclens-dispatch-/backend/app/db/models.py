# backend/app/db/models.py
# Database table definitions using SQLAlchemy
# Defines the structure of all tables in the database
#
# Day 48: Added image_caption column for vision model output
# Day 56: Added database indexes for query performance
#
# Indexes speed up queries that filter, sort, or search by specific columns.
# Without indexes, the database scans every row (slow for large datasets).
# With indexes, the database uses a sorted lookup table (fast).

# Import SQLAlchemy components for defining table structure
import sqlalchemy

# Import individual column types and index
from sqlalchemy import (
    Table,          # Represents a database table
    Column,         # Represents a column in a table
    Integer,        # Integer data type (for IDs, counts)
    String,         # Text/string data type
    Float,          # Decimal number type (for risk scores)
    DateTime,       # Date and time type
    MetaData,       # Container that holds table definitions together
    Index,          # Database index for faster queries
)

# Import datetime for setting default timestamps
from datetime import datetime, timezone


# ========================================
# METADATA
# ========================================

# MetaData is a container that holds all table definitions
# It's used by SQLAlchemy to know about the database structure
metadata = sqlalchemy.MetaData()


# ========================================
# INCIDENTS TABLE
# ========================================

# Define the incidents table structure
# Each row represents one incident report
incidents = Table(
    "incidents",    # Table name in the database
    metadata,       # Register this table with our metadata

    # --- Core fields ---

    # Primary key — unique identifier, auto-incremented
    Column("id", Integer, primary_key=True, autoincrement=True),

    # Source of the report (e.g., "citizen", "dispatcher", "sensor")
    Column("source", String, nullable=True),

    # Text description of what happened
    Column("description", String, nullable=False),

    # Location where the incident occurred
    Column("location", String, nullable=True),

    # When the incident was created in the database
    # default=datetime.utcnow sets this automatically on insert
    Column("created_at", DateTime, default=lambda: datetime.now(timezone.utc)),

    # --- File upload paths ---

    # Path to uploaded audio file (None if no audio)
    Column("audio_path", String, nullable=True),

    # Path to uploaded image file (None if no image)
    Column("image_path", String, nullable=True),

    # --- AI-generated fields ---

    # Audio transcript from Whisper ASR (Day 34)
    Column("transcript", String, nullable=True),

    # AI-generated summary from BART-Large-CNN (Day 47)
    Column("summary", String, nullable=True),

    # Risk score from BART-MNLI (Day 45) — float between 0.0 and 1.0
    Column("risk_score", Float, nullable=True),

    # Incident type from BART-MNLI (Day 46)
    # Values: "fire", "medical", "traffic", "crime", "noise", "infrastructure", "other"
    Column("incident_type", String, nullable=True),

    # Severity level from BART-MNLI (Day 46)
    # Values: "high", "medium", "low"
    Column("severity", String, nullable=True),

    # Image caption from DETR object detection (Day 48)
    Column("image_caption", String, nullable=True),

    # Dispatcher-managed status of this incident
    # Values: "pending" (new, unhandled), "active" (being handled), "resolved" (closed)
    Column("status", String, default="pending", nullable=False),
)


# ========================================
# DATABASE INDEXES (Day 56)
# ========================================
# Indexes speed up queries that filter or sort by these columns.
# Each index creates a sorted lookup table for that column.
#
# How to read these:
#   Index("idx_name", table.c.column)
#   "idx_name" is just a label — it doesn't affect functionality
#   table.c.column is the column to index
#
# When the database sees WHERE incident_type = 'fire',
# it uses the idx_incident_type index to jump directly to fire rows
# instead of scanning every row.

# Index on incident_type — used by the type filter dropdown
# Speeds up: WHERE incident_type = 'fire'
idx_incident_type = Index("idx_incident_type", incidents.c.incident_type)

# Index on severity — used by severity filtering
# Speeds up: WHERE severity = 'high'
idx_severity = Index("idx_severity", incidents.c.severity)

# Index on risk_score — used when sorting by risk
# Speeds up: ORDER BY risk_score DESC
idx_risk_score = Index("idx_risk_score", incidents.c.risk_score)

# Index on created_at — used by default sort (newest first)
# This is the most important index because the dashboard always sorts by time
# Speeds up: ORDER BY created_at DESC
idx_created_at = Index("idx_created_at", incidents.c.created_at)