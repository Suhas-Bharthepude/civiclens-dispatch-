# backend/tests/test_incidents.py
# This file tests incident-related endpoints with database operations

# Import pytest for testing
import pytest

# Import asyncio for async test support
import asyncio

# Import TestClient from FastAPI
from fastapi.testclient import TestClient

# Import our app and database
from app.main import app
from app.db.database import database, metadata, engine

# Import incidents table for cleanup
from app.db.models import incidents


# ========================================
# FIXTURES - Test Setup and Cleanup
# ========================================

@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """
    This is a FIXTURE - a special function that runs before/after each test.
    
    What it does:
    1. BEFORE each test: Creates fresh database tables
    2. Runs the test
    3. AFTER each test: Cleans up the database
    
    Think of it like:
    - Setting up a clean room before a guest arrives
    - Guest uses the room (test runs)
    - Cleaning up after guest leaves
    
    The 'autouse=True' means this runs automatically for every test.
    """
    # SETUP: Create all tables
    # This ensures we start with a clean database for each test
    metadata.create_all(engine)
    
    # Connect to database
    await database.connect()
    
    # Clear any existing data
    # This makes sure tests don't affect each other
    await database.execute(incidents.delete())
    
    # YIELD: This is where the test runs
    # Everything above runs BEFORE the test
    # Everything below runs AFTER the test
    yield
    
    # TEARDOWN: Disconnect from database
    await database.disconnect()


# Create a test client
# This is like a fake browser for testing
client = TestClient(app)


# ========================================
# LESSON 6: Testing POST Requests (Creating Data)
# ========================================

def test_create_incident():
    """
    Test creating a new incident via POST /incidents
    
    This tests:
    1. We can send data to the API
    2. The API validates the data (Pydantic)
    3. The data is saved to the database
    4. We get back a proper response with the created incident
    """
    # ARRANGE: Prepare the incident data
    # This is the JSON we'll send in the request body
    incident_data = {
        "source": "test_user",  # Who reported it
        "description": "Test incident for pytest",  # What happened
        "location": "123 Test Street"  # Where it happened
    }
    
    # ACT: Send POST request to create incident
    # client.post() sends a POST request
    # json=incident_data automatically converts dict to JSON
    response = client.post("/incidents", json=incident_data)
    
    # ASSERT: Check the response
    # Status code 201 means "Created" - resource was successfully created
    assert response.status_code == 201
    
    # Parse response JSON
    data = response.json()
    
    # Check all expected fields are in response
    assert "id" in data  # Should have auto-generated ID
    assert data["source"] == "test_user"  # Check source matches
    assert data["description"] == "Test incident for pytest"  # Check description
    assert data["location"] == "123 Test Street"  # Check location
    
    # Check AI fields are None (not processed yet)
    assert data["transcript"] is None
    assert data["summary"] is None
    assert data["risk_score"] is None


def test_create_incident_missing_required_field():
    """
    Test that creating an incident without required fields fails.
    
    This tests that our Pydantic validation works!
    """
    # ARRANGE: Create incident data MISSING the 'description' field
    # This should fail because description is required
    incomplete_data = {
        "source": "test_user",
        "location": "123 Test Street"
        # description is MISSING!
    }
    
    # ACT: Try to create incident with incomplete data
    response = client.post("/incidents", json=incomplete_data)
    
    # ASSERT: Should return 422 (Unprocessable Entity)
    # 422 means "I understand your request, but the data is invalid"
    assert response.status_code == 422


# ========================================
# LESSON 7: Testing GET Requests (Reading Data)
# ========================================

def test_list_incidents_empty():
    """
    Test GET /incidents when database is empty.
    
    Should return empty list with status 200.
    """
    # ACT: Get all incidents
    response = client.get("/incidents")
    
    # ASSERT: Should succeed with empty list
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)  # Check it's a list
    assert len(data) == 0  # Check it's empty


def test_list_incidents_with_data():
    """
    Test GET /incidents when we have incidents in database.
    
    This test:
    1. Creates an incident first
    2. Then lists all incidents
    3. Checks the created incident is in the list
    """
    # ARRANGE: Create an incident first
    incident_data = {
        "source": "citizen",
        "description": "Fire on Main St",
        "location": "123 Main St"
    }
    
    # Create the incident
    create_response = client.post("/incidents", json=incident_data)
    assert create_response.status_code == 201  # Make sure it was created
    
    created_incident = create_response.json()
    incident_id = created_incident["id"]  # Save the ID
    
    # ACT: Now get all incidents
    list_response = client.get("/incidents")
    
    # ASSERT: Check we get our incident back
    assert list_response.status_code == 200
    
    incidents_list = list_response.json()
    assert len(incidents_list) == 1  # Should have exactly 1 incident
    
    # Check the incident in the list matches what we created
    first_incident = incidents_list[0]
    assert first_incident["id"] == incident_id
    assert first_incident["description"] == "Fire on Main St"


def test_get_single_incident():
    """
    Test GET /incidents/{id} to retrieve one specific incident.
    """
    # ARRANGE: Create an incident first
    incident_data = {
        "source": "police",
        "description": "Car accident",
        "location": "Highway 101"
    }
    
    create_response = client.post("/incidents", json=incident_data)
    created_incident = create_response.json()
    incident_id = created_incident["id"]
    
    # ACT: Get the specific incident by ID
    response = client.get(f"/incidents/{incident_id}")
    
    # ASSERT: Check we got the right incident
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == incident_id
    assert data["description"] == "Car accident"


def test_get_nonexistent_incident():
    """
    Test GET /incidents/{id} with an ID that doesn't exist.
    
    Should return 404 Not Found.
    """
    # ACT: Try to get incident with ID 99999 (doesn't exist)
    response = client.get("/incidents/99999")
    
    # ASSERT: Should return 404
    assert response.status_code == 404


# ========================================
# LESSON 8: Testing Query Parameters (Filtering)
# ========================================

def test_filter_incidents_by_source():
    """
    Test filtering incidents by source using query parameters.
    
    Example: GET /incidents?source=citizen
    """
    # ARRANGE: Create multiple incidents with different sources
    incidents_to_create = [
        {"source": "citizen", "description": "Fire", "location": "123 St"},
        {"source": "police", "description": "Accident", "location": "456 Ave"},
        {"source": "citizen", "description": "Flood", "location": "789 Rd"}
    ]
    
    # Create all incidents
    for incident_data in incidents_to_create:
        response = client.post("/incidents", json=incident_data)
        assert response.status_code == 201
    
    # ACT: Filter for only 'citizen' incidents
    # This adds ?source=citizen to the URL
    response = client.get("/incidents?source=citizen")
    
    # ASSERT: Should only get citizen incidents
    assert response.status_code == 200
    
    filtered_incidents = response.json()
    assert len(filtered_incidents) == 2  # Should have 2 citizen incidents
    
    # Check all returned incidents are from citizen
    for incident in filtered_incidents:
        assert incident["source"] == "citizen"


def test_pagination():
    """
    Test pagination with limit and offset parameters.
    
    Example: GET /incidents?limit=2&offset=1
    """
    # ARRANGE: Create 5 incidents
    for i in range(5):
        incident_data = {
            "source": "test",
            "description": f"Incident {i+1}",
            "location": f"Location {i+1}"
        }
        client.post("/incidents", json=incident_data)
    
    # ACT: Get only 2 incidents (limit=2)
    response = client.get("/incidents?limit=2")
    
    # ASSERT: Should get exactly 2 incidents
    assert response.status_code == 200
    
    incidents = response.json()
    assert len(incidents) == 2  # Only 2 incidents returned
    
    # ACT: Get next page (skip first incident, get 2 more)
    response_page2 = client.get("/incidents?limit=2&offset=1")
    incidents_page2 = response_page2.json()
    
    # ASSERT: Should get different incidents
    assert len(incidents_page2) == 2
    # First incident on page 2 should be different from page 1
    assert incidents_page2[0]["id"] != incidents[0]["id"]