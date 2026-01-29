# This file is about “What does my data look like in the database?”

# Import SQlAlchemy column types
from sqlalchemy import Table, Column, Integer, String, Float

# Import metadata so this table gets registered
# .database in Python is a form of relative import, which allows you to import modules or packages located within the same package structure as the current file
from app.db.database import metadata

# Define a table called "incidents"
# This maps directly to a SQL table



incidents = Table(
    "incidents",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("source", String, nullable=False),
    Column("description", String, nullable=False),
    Column("audio_path", String, nullable=True),
    Column("transcript", String, nullable=True),
    Column("summary", String, nullable=True),
    Column("risk_score", Float, nullable=True),
)


 # NULL means no value, missing, etc.
    # nullable=False prevents NULL, but does NOT prevent empty strings

