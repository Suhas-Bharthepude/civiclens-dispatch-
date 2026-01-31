-- ============================
-- CREATE TABLE
-- ============================


-- CREATE TABLE starts a new table definition in the database 
-- incidents is the name of that table 
CREATE TABLE incidents (
    -- id is the column name; INTEGER is the data type for whole numbers
    -- PRIMARY KEY means this column uniquely identifiies each row and is indexed   
    id INTEGER PRIMARY KEY,  
    
    -- description is the column name; TEXT stores variable-length text
    -- NOT NULL means this column must always have a value (cannot be empty)
    description TEXT NOT NULL,

    -- location is the column name; TEXT for storing text like city, address
    -- NOT NULL means this column must always have a value (cannot be empty)
    location TEXT NOT NULL,

    -- source is the column name; TEXT for who the incident info came from 
    -- NOT NULL means source is required for every row
    source TEXT NOT NULL,

    -- risk_score is the column name; REAL is a floating-point number (ex: 3.5, 7.2)
    risk_score REAL, 

    -- transcript is the column name; TEXT for long bodies of text
    -- no NOT NULL here, so its not required
    transcript TEXT,

    -- summary is the column name; TEXT for a shorter summary of the incident 
    -- also optional because NOT NULL is not specified
    summary TEXT

    -- ); closes the CREATE TABLE statement and ends the table defintion 

);


-- ============================
-- INSERT DATA
-- ============================

-- INSERT INTO tells the database you want to add a new row into a table.
-- incidents is the name of the table you're inserting data into.
INSERT INTO incidents (
    
    -- description is the column that will receive a value (text describing the incident).
    description,
   
    -- location is the column for where the incident happened.
    location,

    -- source is the column for who/what reported or generated the incident.
    source,

    -- risk_score is the column for a numeric risk value (can be NULL if unknown).
    risk_score,

    -- transcript is the column for a longer text record (like a call transcript).
    transcript,
    
    -- summary is the column for a short text summary of the incident.
    summary


    -- VALUES introduces the actual data you want to insert into the listed columns,
    -- in the exact same order as the column names above.
) VALUES (

    -- 'Fire in office' is the value for description (a string literal).
    'Fire in office',
    
    -- '200 Broadway Ave' is the value for location.
    '200 Broadway Ave',
    
    -- 'citizen' is the value for source (who reported it).
    'citizen',
    
    -- NULL means "no value" or "unknown" for risk_score (not 0, just empty). 
    NULL,

    -- NULL for transcript means there is currently no transcript stored.
    NULL,
   
    -- NULL for summary means no summary has been provided yet.
    NULL
);


-- Insert another row into the incidents table
INSERT INTO incidents (
    
    -- Description of the incident
    description,
    
    -- Where it happened
    location,
    
    -- Who reported it
    source

) VALUES (
    -- Value for description
    'Medical emergency',
    
    -- Value for location
    '15 Pine Street',
    
    -- Value for source
    'dispatcher'
    
    -- Missing columns (risk_score, transcript, summary)
    -- will automatically become NULL
);
-- You don’t insert id → database generates it
-- Columns omitted default to NULL
-- Multiple INSERTs create multiple rows


-- ============================
-- SELECT DATA (reading data)
-- ============================

-- SELECT is used to read data from a table. 
-- * means "all columns" from the table. 
-- FROM tells SQL which table to read from. 
-- incidents is the name of the table.SELECT * FROM incidents;
SELECT * FROM incidents;

-- SELECT here is again to read data
-- This time, instead of *, we list specific columns we want
-- id, description, location are the column names to return 
SELECT id, description, location


-- FROM specifies which table to read those columns from.
-- incidents is the table we are querying
FROM incidents


-- WHERE filters the rows: only rows that match this condition are returned. 
-- source = 'citizen' means: only rows where the source column 
-- has the exact text value 'citizen'. WHERE source = 'citizen';
WHERE source = 'citizen';

-- ============================
-- UPDATE DATA
-- ============================

UPDATE incidents -- modifies existing rows
SET risk_score = 0.87 -- which columns change
WHERE id = 1; -- which rows are affected


-- ============================
-- DELETE DATA
-- ============================

DELETE FROM incidents -- removes rows permanently from incidents 
WHERE id = 2; 