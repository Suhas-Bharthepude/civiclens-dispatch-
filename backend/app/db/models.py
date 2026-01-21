# This file is about “What does my data look like in the database?”

# Import SQlAlchemy column types
from sqlalchemy import Table, Column, Integer, String, Float

# Import metadata so this table gets registered
# .database in Python is a form of relative import, which allows you to import modules or packages located within the same package structure as the current file
from app.db.database import metadata

# Define a table called "incidents"
# This maps directly to a SQL table

incidents = Table(
    "incidents",            # table name
    metadata,               # metadata object
    Column("id", Integer, primary_key=True),   # unique id
    Column("description", String, nullable=False), # description text
    Column("location", String, nullable=False),    # location text
    Column("source", String, nullable=False),      # source of report
    Column("risk_score", Float, nullable=True),   # optional AI-calculated risk
    Column("transcript", String, nullable=True),  # optional audio transcript
    Column("summary", String, nullable=True),     # optional AI summary
)

 # NULL means no value, missing, etc.
    # nullable=False prevents NULL, but does NOT prevent empty strings

