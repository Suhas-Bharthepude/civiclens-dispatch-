# Database Concepts for CivicLens Dispatch

## What is a Database?
A **database** is an organized collection of structured data that can be easily accessed, managed, and updated. Think of it as an electronic filing system.

## Key Database Concepts

### Table
A **table** is a collection of related data organized in rows and columns, like a spreadsheet.

Example: `incidents` table stores all incident reports.

### Schema
A **schema** is the structure/blueprint of a database. It defines:
- What tables exist
- What columns each table has
- Data types for each column
- Relationships between tables

### Row (Record)
A **row** (also called a record) represents a single entry in a table.

Example: One incident report = one row in the incidents table.

### Column (Field)
A **column** (also called a field) represents a specific attribute of the data.

Example: `description`, `location`, `severity` are columns in incidents table.

### Primary Key
A **primary key** is a unique identifier for each row in a table.

- Must be unique (no duplicates)
- Cannot be NULL
- Usually auto-incremented

Example: `id` column in incidents table (1, 2, 3, 4...)

### Foreign Key
A **foreign key** is a column that references the primary key of another table, creating a relationship between tables.

Example (future):
- `incidents` table has `dispatcher_id` column
- References `id` in `users` table
- Links each incident to the dispatcher who handled it

## CivicLens Database Schema

### Incidents Table

```sql
CREATE TABLE incidents (
    -- Primary Key
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    
    -- Core Fields (Required)
    source VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    location VARCHAR(255) NOT NULL,
    
    -- Media Paths (Optional)
    audio_path VARCHAR(500),
    image_path VARCHAR(500),
    
    -- AI-Generated Fields (Optional)
    transcript TEXT,
    summary TEXT,
    risk_score REAL,
    incident_type VARCHAR(100),
    severity VARCHAR(50)
);
```

### Data Types

- **INTEGER**: Whole numbers (1, 2, 3, 100)
- **VARCHAR(n)**: Variable-length text up to n characters
- **TEXT**: Long text with no practical limit
- **REAL**: Floating-point numbers (0.5, 3.14, 0.87)

### Constraints

- **NOT NULL**: Column must have a value
- **PRIMARY KEY**: Unique identifier for rows
- **AUTOINCREMENT**: Database automatically assigns next number

## PostgreSQL vs SQLite

### SQLite (Current - Development)
- File-based database (test.db file)
- No separate server needed
- Great for development and testing
- Limited concurrent writes

### PostgreSQL (Production)
- Server-based database
- Better performance at scale
- Better concurrent access
- Industry standard for web apps

## Why We Use Both Drivers

### asyncpg (Async Operations)
```python
# For all CRUD operations in routes
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
```
- Non-blocking database queries
- Better performance in async FastAPI
- Used by `databases` library

### psycopg2 (Sync Operations)
```python
# For table creation only
engine = create_engine(sync_db_url)
metadata.create_all(engine)
```
- Synchronous operations
- Used by SQLAlchemy's `create_all()` method
- Runs once at startup

## Query Examples

### INSERT (Create)
```python
query = incidents.insert().values(
    source="citizen",
    description="Fire reported",
    location="123 Main St"
)
incident_id = await database.execute(query)
```

### SELECT (Read)
```python
# Get all incidents
query = incidents.select()
results = await database.fetch_all(query)

# Get one incident
query = incidents.select().where(incidents.c.id == 5)
incident = await database.fetch_one(query)
```

### UPDATE (Modify)
```python
query = (
    incidents
    .update()
    .where(incidents.c.id == 5)
    .values(severity="high")
)
await database.execute(query)
```

### DELETE (Remove)
```python
query = incidents.delete().where(incidents.c.id == 5)
await database.execute(query)
```

## Connection String Format

```
postgresql+asyncpg://USERNAME:PASSWORD@HOST:PORT/DATABASE
│                   │        │         │    │    │
│                   │        │         │    │    └─ Database name
│                   │        │         │    └────── Port (5432 default)
│                   │        │         └─────────── Server address
│                   │        └───────────────────── Password
│                   └────────────────────────────── Username
└────────────────────────────────────────────────── Driver (asyncpg)
```

---

*This document explains core database concepts used in CivicLens Dispatch*


