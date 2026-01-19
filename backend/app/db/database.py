# This file is about “How does my app talk to the database?”
<<<<<<< HEAD
=======
# PostgreSQl connection that reads from .env

>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)


# Import necessary libraries
# pip install sqlalchemy databases aiosqlite
# sqlalchemy -> lets us define Python classes that map to database tables. That's why it's called an ORM
# databases -> async library to let FastAPI talk to SQL databases without blocking
# aiosqlite -> async driver for SQLite so the database can work with async requests 


<<<<<<< HEAD



# Import Database from databases library (async support)
from databases import Database


# Import the engine creator from SQLAlchemy
# The engine is the low-level connection to the database
# We need these to define tables and connect Python to the database.
=======
# standard python library for working with environment variables and file paths
import os


# Import Database from databases library (async support)
# Async library that allows FastAPI to talk to databases without blocking other requests

from databases import Database


# SQLAlchemy is an ORM: lets Python know about tables and handle SQL behind the scenes

>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
from sqlalchemy import create_engine, MetaData


# Create the connection string for SQLite
# sqlite:/// means "SQLite database"
# ./incidents.db means "store it as a file next to this code"
# SQLite stores data in a local file
# Tells SQLAlchemy and FastAPI where the data file is ./ means it will be created backend/app
<<<<<<< HEAD
DATABASE_URL = "sqlite:///./incidents.db"


# This Database object is what routes will use
# It supports async queries (await)
database = Database(DATABASE_URL) 


# The engine is used by SQLAlchemy to CREATE tables
# SQLite needs this extra augment for async safety 
engine = create_engine(DATABASE_URL)


# Metadata stores table defintions
# Think of it as a registry of tables 
=======
# DATABASE_URL = "sqlite:///./incidents.db" not needed anymore


# Loads environment variables from a .env file
from dotenv import load_dotenv



# Load environment variables from .env
load_dotenv() # Reads backend/.env



# Get the database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL") 

# Async database object for FastAPI endpoints
database = Database(DATABASE_URL)

# SQLAlchemy sync engine for table creation
# SQLAlchemy cannot use asyncpg directly, so replace it with psycopg2
engine = create_engine(
    DATABASE_URL.replace("asyncpg", "psycopg2"), echo=True
)



# Metadata registry for SQLAlchemy models
# Metadata stores table defintions
# It as a registry of tables; keeps incidents table there
# All your tables defined in models.py will use this metadata
>>>>>>> 585adbd (Day 12: Integrated FastAPI with PostgreSQL, moved backend to main repo)
metadata = MetaData()





