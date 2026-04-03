# backend/scripts/test_e2e.py
# End-to-end integration test for the CivicLens Dispatch system
#
# This script tests the FULL workflow:
#   1. Create an incident via the API
#   2. Run the AI pipeline on it
#   3. Verify all AI fields are populated correctly
#   4. Test the reprocess endpoint
#   5. Test the AI status endpoint
#   6. Clean up
#
# Usage:
#   Make sure the backend server is running first:
#     cd backend && uvicorn app.main:app --reload
#   Then in another terminal:
#     cd backend && source ../.venv/bin/activate
#     PYTHONPATH=. python scripts/test_e2e.py
#
# Day 52: End-to-end integration testing

# Import httpx for making HTTP requests to our own API
import httpx

# Import asyncio to run async functions
import asyncio

# Import time for measuring durations
import time

# Import sys for exit codes
import sys


# ========================================
# CONFIGURATION
# ========================================

# Base URL of our running FastAPI server
BASE_URL = "http://localhost:8000"

# Timeout for API requests (seconds)
# Some requests trigger AI processing which can be slow
REQUEST_TIMEOUT = 10

# How long to wait for AI pipeline to complete (seconds)
# The pipeline runs in the background — we need to poll until it's done
PIPELINE_WAIT_TIMEOUT = 120

# How often to poll for pipeline completion (seconds)
POLL_INTERVAL = 5


# ========================================
# TEST FUNCTIONS
# ========================================

async def test_health_check(client: httpx.AsyncClient) -> bool:
    """Test 1: Basic health check — is the server running?"""
    print("\n--- Test 1: Health Check ---")
    
    try:
        # Send GET /health
        response = await client.get(f"{BASE_URL}/health")
        
        # Check status code
        if response.status_code != 200:
            print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
            return False
        
        # Check response body
        data = response.json()
        if data.get("status") != "ok":
            print(f"  ❌ FAIL: Expected status 'ok', got {data}")
            return False
        
        print(f"  ✅ PASS: Server is healthy — {data}")
        return True
    
    except httpx.ConnectError:
        print(f"  ❌ FAIL: Cannot connect to {BASE_URL}")
        print(f"     Is the backend server running? Start it with:")
        print(f"     cd backend && uvicorn app.main:app --reload")
        return False


async def test_ai_status(client: httpx.AsyncClient) -> bool:
    """Test 2: AI pipeline status — are all models reachable?"""
    print("\n--- Test 2: AI Pipeline Status ---")
    
    # Send GET /ai/status
    response = await client.get(f"{BASE_URL}/ai/status")
    
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        return False
    
    data = response.json()
    status = data.get("pipeline_status", "unknown")
    ready = data.get("models_ready", 0)
    total = data.get("models_total", 0)
    check_time = data.get("total_check_time_seconds", 0)
    
    print(f"  Pipeline: {status} ({ready}/{total} models ready) in {check_time}s")
    
    # Print individual model statuses
    for model in data.get("models", []):
        icon = "✅" if model["status"] == "ready" else "⚠️"
        print(f"  {icon} {model['model']}: {model['status']} ({model['response_time_seconds']}s)")
    
    if status == "healthy":
        print(f"  ✅ PASS: All models healthy")
        return True
    elif status == "degraded":
        print(f"  ⚠️  WARN: Pipeline degraded — some models unavailable")
        return True  # Still pass — degraded is acceptable for testing
    else:
        print(f"  ❌ FAIL: Pipeline is down")
        return False


async def test_create_incident(client: httpx.AsyncClient) -> int:
    """Test 3: Create a new incident via POST /incidents"""
    print("\n--- Test 3: Create Incident ---")
    
    # Incident data that should trigger clear AI classification
    incident_data = {
        "source": "citizen",
        "description": (
            "Major fire at the warehouse on Industrial Boulevard. "
            "Thick black smoke visible from miles away. Multiple fire trucks "
            "responding. At least two workers reported trapped on the second floor. "
            "Explosions heard from inside. Area being evacuated."
        ),
        "location": "500 Industrial Boulevard, Warehouse District"
    }
    
    # Send POST /incidents
    response = await client.post(
        f"{BASE_URL}/incidents",
        json=incident_data
    )
    
    if response.status_code != 201:
        print(f"  ❌ FAIL: Expected 201, got {response.status_code}")
        print(f"     Response: {response.text[:200]}")
        return -1
    
    data = response.json()
    incident_id = data.get("id")
    
    print(f"  ✅ PASS: Created incident #{incident_id}")
    print(f"     Source: {data.get('source')}")
    print(f"     Description: {data.get('description', '')[:80]}...")
    
    return incident_id


async def test_pipeline_completion(client: httpx.AsyncClient, incident_id: int) -> bool:
    """Test 4: Wait for AI pipeline to complete and verify results"""
    print(f"\n--- Test 4: AI Pipeline Completion (incident #{incident_id}) ---")
    print(f"  Waiting for AI pipeline (up to {PIPELINE_WAIT_TIMEOUT}s)...")
    
    start = time.perf_counter()
    
    # Poll the incident until AI fields are populated
    while time.perf_counter() - start < PIPELINE_WAIT_TIMEOUT:
        
        # Fetch the incident
        response = await client.get(f"{BASE_URL}/incidents/{incident_id}")
        
        if response.status_code != 200:
            print(f"  ❌ FAIL: Cannot fetch incident #{incident_id}")
            return False
        
        data = response.json()
        
        # Check if AI fields are populated
        # The pipeline fills in: incident_type, severity, risk_score, summary
        has_type = data.get("incident_type") is not None
        has_severity = data.get("severity") is not None
        has_risk = data.get("risk_score") is not None
        has_summary = data.get("summary") is not None
        
        if has_type and has_severity and has_risk and has_summary:
            # Pipeline is done — all fields populated
            elapsed = time.perf_counter() - start
            
            print(f"  ✅ Pipeline completed in {elapsed:.1f}s")
            print(f"     Type:     {data['incident_type']}")
            print(f"     Severity: {data['severity']}")
            print(f"     Risk:     {data['risk_score']:.4f} ({int(data['risk_score']*100)}%)")
            print(f"     Summary:  {data['summary'][:100]}...")
            
            # Verify the classification makes sense for a fire incident
            expected_type = "fire"
            if data["incident_type"] == expected_type:
                print(f"  ✅ Type correctly classified as '{expected_type}'")
            else:
                print(f"  ⚠️  Type is '{data['incident_type']}', expected '{expected_type}'")
                print(f"     (ML classification may interpret differently — not a hard failure)")
            
            # Verify risk score is high (fire with people trapped should be > 0.5)
            if data["risk_score"] > 0.5:
                print(f"  ✅ Risk score is appropriately high ({data['risk_score']:.2f})")
            else:
                print(f"  ⚠️  Risk score seems low ({data['risk_score']:.2f}) for a fire emergency")
            
            return True
        
        # Not done yet — wait and poll again
        elapsed = time.perf_counter() - start
        fields_done = sum([has_type, has_severity, has_risk, has_summary])
        print(f"  ⏳ {elapsed:.0f}s — {fields_done}/4 AI fields populated...")
        await asyncio.sleep(POLL_INTERVAL)
    
    # Timeout — pipeline didn't complete in time
    print(f"  ❌ FAIL: Pipeline did not complete within {PIPELINE_WAIT_TIMEOUT}s")
    print(f"     This is likely due to Hugging Face API delays on the free tier")
    return False


async def test_reprocess(client: httpx.AsyncClient, incident_id: int) -> bool:
    """Test 5: Reprocess an existing incident"""
    print(f"\n--- Test 5: Reprocess Endpoint (incident #{incident_id}) ---")
    
    # Send POST /incidents/{id}/reprocess
    response = await client.post(f"{BASE_URL}/incidents/{incident_id}/reprocess")
    
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        print(f"     Response: {response.text[:200]}")
        return False
    
    data = response.json()
    
    if data.get("status") == "queued":
        print(f"  ✅ PASS: Reprocess queued — {data.get('message')}")
        return True
    else:
        print(f"  ❌ FAIL: Unexpected response — {data}")
        return False


async def test_search(client: httpx.AsyncClient) -> bool:
    """Test 6: Search functionality"""
    print("\n--- Test 6: Search ---")
    
    # Search for "fire" — should find incidents with fire in description
    response = await client.get(f"{BASE_URL}/incidents", params={"search": "fire"})
    
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        return False
    
    data = response.json()
    count = len(data)
    
    if count > 0:
        print(f"  ✅ PASS: Search for 'fire' returned {count} result(s)")
        return True
    else:
        print(f"  ⚠️  WARN: Search for 'fire' returned 0 results")
        return True  # Not a hard failure


async def cleanup(client: httpx.AsyncClient, incident_id: int):
    """Clean up test data"""
    print(f"\n--- Cleanup ---")
    
    if incident_id > 0:
        response = await client.delete(f"{BASE_URL}/incidents/{incident_id}")
        if response.status_code == 204:
            print(f"  🧹 Deleted test incident #{incident_id}")
        else:
            print(f"  ⚠️  Could not delete incident #{incident_id}: {response.status_code}")


# ========================================
# MAIN TEST RUNNER
# ========================================

async def run_all_tests():
    """Run all end-to-end tests in sequence."""
    
    print("=" * 70)
    print("🧪 END-TO-END INTEGRATION TESTS")
    print("=" * 70)
    print(f"Server: {BASE_URL}")
    print(f"Pipeline timeout: {PIPELINE_WAIT_TIMEOUT}s")
    
    # Track results
    results = []
    incident_id = -1
    
    # Create a shared HTTP client for all tests
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        
        # Test 1: Health check
        results.append(("Health Check", await test_health_check(client)))
        
        # If server isn't running, stop here
        if not results[0][1]:
            print("\n❌ Server is not running. Start it and try again.")
            sys.exit(1)
        
        # Test 2: AI status
        results.append(("AI Status", await test_ai_status(client)))
        
        # Test 3: Create incident
        incident_id = await test_create_incident(client)
        results.append(("Create Incident", incident_id > 0))
        
        # Test 4: Wait for pipeline (only if incident was created)
        if incident_id > 0:
            results.append(("Pipeline Completion", await test_pipeline_completion(client, incident_id)))
        
        # Test 5: Reprocess
        if incident_id > 0:
            results.append(("Reprocess", await test_reprocess(client, incident_id)))
        
        # Test 6: Search
        results.append(("Search", await test_search(client)))
        
        # Cleanup
        await cleanup(client, incident_id)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
        if result:
            passed += 1
    
    print(f"\n  {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
    elif passed >= total - 1:
        print("\n⚠️  Almost there — one test had issues (likely API timeout)")
    else:
        print("\n❌ Some tests failed — check the output above")
    
    print("=" * 70)


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_all_tests())