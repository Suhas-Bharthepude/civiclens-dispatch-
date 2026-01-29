# This file is about “How does my app talk to the database?”


# Import necessary libraries
# pip install sqlalchemy databases aiosqlite
# sqlalchemy -> lets us define Python classes that map to database tables. That's why it's called an ORM
# databases -> async library to let FastAPI talk to SQL databases without blocking
# aiosqlite -> async driver for SQLite so the database can work with async requests 



import os


# Import Database from databases library (async support)
from databases import Database


# Import the engine creator from SQLAlchemy
# The engine is the low-level connection to the database
# We need these to define tables and connect Python to the database.
from sqlalchemy import create_engine, MetaData

# Create the connection string for SQLite
# sqlite:/// means "SQLite database"
# ./incidents.db means "store it as a file next to this code"
# SQLite stores data in a local file
# Tells SQLAlchemy and FastAPI where the data file is ./ means it will be created backend/app

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./incidents.db"
)


# This Database object is what routes will use
# It supports async queries (await)
database = Database(DATABASE_URL) 



# Metadata stores table defintions
# Think of it as a registry of tables 
metadata = MetaData()


# The engine is used by SQLAlchemy to CREATE tables
# SQLite needs this extra augment for async safety 
engine = create_engine(
    DATABASE_URL.replace("+asyncpg", ""),
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)


