# backend/tests/test_api.py
# This file tests our FastAPI endpoints

# Import pytest for testing
import pytest

# Import TestClient from FastAPI
# TestClient lets us test our API without starting the server
from fastapi.testclient import TestClient

# Import our FastAPI app
from app.main import app


# ========================================
# LESSON 4: Testing FastAPI Endpoints
# ========================================

# Create a TestClient instance
# This is like a fake browser that can call our API
client = TestClient(app)


def test_root_endpoint():
    """
    Test the root endpoint: GET /
    
    This test:
    1. Sends a GET request to /
    2. Checks the status code is 200 (OK)
    3. Checks the response contains expected data
    """
    # ACT: Send GET request to root endpoint
    # client.get("/") is like opening http://localhost:8000/ in a browser
    response = client.get("/")
    
    # ASSERT: Check status code
    # Status code 200 means "OK" - request succeeded
    assert response.status_code == 200
    
    # ASSERT: Check response body (JSON)
    # response.json() converts JSON response to Python dict
    data = response.json()
    
    # Check the response has expected keys
    assert "message" in data  # Check 'message' key exists
    assert "version" in data  # Check 'version' key exists
    assert data["version"] == "1.0.0"  # Check version is correct


def test_health_endpoint():
    """
    Test the health check endpoint: GET /health
    
    This is important because:
    - Load balancers use /health to check if server is running
    - Monitoring tools ping /health regularly
    """
    # ACT: Send GET request to /health
    response = client.get("/health")
    
    # ASSERT: Check status code is 200
    assert response.status_code == 200
    
    # ASSERT: Check response data
    data = response.json()
    assert data["status"] == "ok"  # Check status is "ok"
    assert "service" in data  # Check service name is included


def test_echo_endpoint():
    """
    Test the echo endpoint: GET /echo/{name}
    
    This tests path parameters work correctly.
    """
    # ACT: Send GET request with path parameter
    # This is like calling: GET /echo/Alice
    response = client.get("/echo/Alice")
    
    # ASSERT: Check response
    assert response.status_code == 200
    
    data = response.json()
    assert data["hello"] == "Alice"  # Check it echoed back "Alice"
    
    # Test with different name
    response2 = client.get("/echo/Bob")
    data2 = response2.json()
    assert data2["hello"] == "Bob"  # Check it works with "Bob" too


def test_incidents_dummy_endpoint():
    """
    Test the dummy incidents endpoint: GET /incidents_dummy
    
    This tests query parameters work correctly.
    """
    # ACT: Send GET request without filter
    response = client.get("/incidents_dummy")
    
    # ASSERT: Check we get incidents back
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)  # Check response is a list
    assert len(data) > 0  # Check list is not empty
    
    # ACT: Send GET request WITH filter
    # This is like calling: GET /incidents_dummy?severity=high
    response_filtered = client.get("/incidents_dummy?severity=high")
    
    # ASSERT: Check filtering works
    assert response_filtered.status_code == 200
    
    filtered_data = response_filtered.json()
    # Check all returned incidents have severity="high"
    for incident in filtered_data:
        assert incident["severity"] == "high"


# ========================================
# LESSON 5: Testing with Different Scenarios
# ========================================

def test_nonexistent_endpoint():
    """
    Test that requesting a non-existent endpoint returns 404.
    
    404 means "Not Found"
    """
    # ACT: Try to access endpoint that doesn't exist
    response = client.get("/this-does-not-exist")
    
    # ASSERT: Should return 404
    assert response.status_code == 404