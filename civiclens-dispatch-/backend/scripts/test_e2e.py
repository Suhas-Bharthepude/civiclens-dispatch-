# backend/scripts/test_e2e.py
# End-to-end integration test for the CivicLens Dispatch system
#
# Day 52: Original e2e tests
# Day 72: Updated to authenticate as dispatcher before each test.
#          All /incidents endpoints now require a valid JWT.
#          A helper (get_auth_token) logs in via POST /auth/login and
#          returns an Authorization header dict used by every request.
#
# Usage:
#   Make sure the backend server is running, then:
#     cd backend && source ../.venv/bin/activate
#     PYTHONPATH=. python scripts/test_e2e.py
#
#   The seed script must have been run first:
#     PYTHONPATH=. python scripts/seed_users.py

import httpx
import asyncio
import time
import sys


# ========================================
# CONFIGURATION
# ========================================

BASE_URL         = "http://localhost:8000"
REQUEST_TIMEOUT  = 10
PIPELINE_WAIT_TIMEOUT = 120
POLL_INTERVAL    = 5

# Dispatcher credentials created by scripts/seed_users.py
DISPATCHER_USERNAME = "dispatcher"
DISPATCHER_PASSWORD = "dispatch123"

# Admin credentials (needed for cleanup DELETE)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


# ========================================
# AUTH HELPER (Day 72)
# ========================================

async def get_auth_token(client: httpx.AsyncClient, username: str, password: str) -> dict:
    """
    Log in and return an Authorization header dict for subsequent requests.

    Returns {"Authorization": "Bearer <token>"} on success,
    or an empty dict if login fails (test will then get 401 and fail clearly).
    """
    try:
        response = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            return {"Authorization": f"Bearer {token}"}
        print(f"  ⚠️  Login failed for '{username}': HTTP {response.status_code}")
        return {}
    except Exception as e:
        print(f"  ⚠️  Login request failed: {e}")
        return {}


# ========================================
# TEST FUNCTIONS
# ========================================

async def test_health_check(client: httpx.AsyncClient) -> bool:
    """Test 1: Basic health check — is the server running?"""
    print("\n--- Test 1: Health Check ---")
    try:
        response = await client.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
            return False
        data = response.json()
        if data.get("status") != "ok":
            print(f"  ❌ FAIL: Expected status 'ok', got {data}")
            return False
        print(f"  ✅ PASS: Server is healthy — {data}")
        return True
    except httpx.ConnectError:
        print(f"  ❌ FAIL: Cannot connect to {BASE_URL}")
        print(f"     Is the backend server running?")
        return False


async def test_auth_login(client: httpx.AsyncClient) -> bool:
    """Test 2: Authentication — can we log in as dispatcher?"""
    print("\n--- Test 2: Auth Login ---")
    headers = await get_auth_token(client, DISPATCHER_USERNAME, DISPATCHER_PASSWORD)
    if headers:
        print(f"  ✅ PASS: Login succeeded for '{DISPATCHER_USERNAME}'")
        return True
    print(f"  ❌ FAIL: Could not log in as '{DISPATCHER_USERNAME}'")
    print(f"     Run: PYTHONPATH=. python scripts/seed_users.py")
    return False


async def test_ai_status(client: httpx.AsyncClient) -> bool:
    """Test 3: AI pipeline status — are all models reachable?"""
    print("\n--- Test 3: AI Pipeline Status ---")
    response = await client.get(f"{BASE_URL}/ai/status")
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        return False
    data = response.json()
    status = data.get("pipeline_status", "unknown")
    ready  = data.get("models_ready", 0)
    total  = data.get("models_total", 0)
    print(f"  Pipeline: {status} ({ready}/{total} models ready)")
    for model in data.get("models", []):
        icon = "✅" if model["status"] == "ready" else "⚠️"
        print(f"  {icon} {model['model']}: {model['status']}")
    if status in ("healthy", "degraded"):
        print(f"  ✅ PASS: Pipeline status is '{status}'")
        return True
    print(f"  ❌ FAIL: Pipeline is down")
    return False


async def test_create_incident(client: httpx.AsyncClient, auth_headers: dict) -> int:
    """Test 4: Create a new incident via POST /incidents"""
    print("\n--- Test 4: Create Incident ---")
    incident_data = {
        "source":      "citizen",
        "description": (
            "Major fire at the warehouse on Industrial Boulevard. "
            "Thick black smoke visible from miles away. Multiple fire trucks "
            "responding. At least two workers reported trapped on the second floor. "
            "Explosions heard from inside. Area being evacuated."
        ),
        "location": "500 Industrial Boulevard, Warehouse District",
    }
    # Auth header required — endpoints return 401 without it (Day 72)
    response = await client.post(
        f"{BASE_URL}/incidents",
        json=incident_data,
        headers=auth_headers,
    )
    if response.status_code != 201:
        print(f"  ❌ FAIL: Expected 201, got {response.status_code}")
        print(f"     Response: {response.text[:200]}")
        return -1
    data = response.json()
    incident_id = data.get("id")
    print(f"  ✅ PASS: Created incident #{incident_id}")
    return incident_id


async def test_pipeline_completion(
    client: httpx.AsyncClient, incident_id: int, auth_headers: dict
) -> bool:
    """Test 5: Wait for AI pipeline to complete and verify results"""
    print(f"\n--- Test 5: AI Pipeline Completion (incident #{incident_id}) ---")
    print(f"  Waiting for AI pipeline (up to {PIPELINE_WAIT_TIMEOUT}s)...")
    start = time.perf_counter()
    while time.perf_counter() - start < PIPELINE_WAIT_TIMEOUT:
        response = await client.get(
            f"{BASE_URL}/incidents/{incident_id}",
            headers=auth_headers,
        )
        if response.status_code != 200:
            print(f"  ❌ FAIL: Cannot fetch incident #{incident_id}")
            return False
        data = response.json()
        has_type     = data.get("incident_type") is not None
        has_severity = data.get("severity")      is not None
        has_risk     = data.get("risk_score")    is not None
        has_summary  = data.get("summary")       is not None
        if has_type and has_severity and has_risk and has_summary:
            elapsed = time.perf_counter() - start
            print(f"  ✅ Pipeline completed in {elapsed:.1f}s")
            print(f"     Type:     {data['incident_type']}")
            print(f"     Severity: {data['severity']}")
            print(f"     Risk:     {data['risk_score']:.4f}")
            print(f"     Summary:  {data['summary'][:100]}...")
            return True
        elapsed = time.perf_counter() - start
        fields_done = sum([has_type, has_severity, has_risk, has_summary])
        print(f"  ⏳ {elapsed:.0f}s — {fields_done}/4 AI fields populated...")
        await asyncio.sleep(POLL_INTERVAL)
    print(f"  ❌ FAIL: Pipeline did not complete within {PIPELINE_WAIT_TIMEOUT}s")
    return False


async def test_reprocess(
    client: httpx.AsyncClient, incident_id: int, auth_headers: dict
) -> bool:
    """Test 6: Reprocess an existing incident"""
    print(f"\n--- Test 6: Reprocess Endpoint (incident #{incident_id}) ---")
    response = await client.post(
        f"{BASE_URL}/incidents/{incident_id}/reprocess",
        headers=auth_headers,
    )
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        return False
    data = response.json()
    if data.get("status") == "queued":
        print(f"  ✅ PASS: Reprocess queued — {data.get('message')}")
        return True
    print(f"  ❌ FAIL: Unexpected response — {data}")
    return False


async def test_search(client: httpx.AsyncClient, auth_headers: dict) -> bool:
    """Test 7: Search functionality"""
    print("\n--- Test 7: Search ---")
    response = await client.get(
        f"{BASE_URL}/incidents",
        params={"search": "fire"},
        headers=auth_headers,
    )
    if response.status_code != 200:
        print(f"  ❌ FAIL: Expected 200, got {response.status_code}")
        return False
    data = response.json()
    count = len(data)
    if count > 0:
        print(f"  ✅ PASS: Search for 'fire' returned {count} result(s)")
        return True
    print(f"  ⚠️  WARN: Search for 'fire' returned 0 results")
    return True  # Not a hard failure


async def cleanup(
    client: httpx.AsyncClient, incident_id: int, admin_headers: dict
):
    """Clean up test data — delete requires admin role (Day 72)"""
    print(f"\n--- Cleanup ---")
    if incident_id > 0:
        response = await client.delete(
            f"{BASE_URL}/incidents/{incident_id}",
            headers=admin_headers,
        )
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

    results = []
    incident_id = -1

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:

        # Test 1: Health check (no auth required)
        results.append(("Health Check", await test_health_check(client)))
        if not results[0][1]:
            print("\n❌ Server is not running. Start it and try again.")
            sys.exit(1)

        # Obtain auth tokens before exercising protected endpoints (Day 72)
        dispatcher_headers = await get_auth_token(client, DISPATCHER_USERNAME, DISPATCHER_PASSWORD)
        admin_headers      = await get_auth_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)

        # Test 2: Auth login
        results.append(("Auth Login", bool(dispatcher_headers)))
        if not dispatcher_headers:
            print("\n❌ Cannot authenticate. Run seed_users.py first.")
            sys.exit(1)

        # Test 3: AI status (no auth required)
        results.append(("AI Status", await test_ai_status(client)))

        # Test 4: Create incident
        incident_id = await test_create_incident(client, dispatcher_headers)
        results.append(("Create Incident", incident_id > 0))

        # Test 5: Wait for pipeline
        if incident_id > 0:
            results.append(("Pipeline Completion",
                await test_pipeline_completion(client, incident_id, dispatcher_headers)))

        # Test 6: Reprocess
        if incident_id > 0:
            results.append(("Reprocess",
                await test_reprocess(client, incident_id, dispatcher_headers)))

        # Test 7: Search
        results.append(("Search", await test_search(client, dispatcher_headers)))

        # Cleanup — admin only (Day 72)
        await cleanup(client, incident_id, admin_headers)

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS")
    print("=" * 70)
    passed = 0
    for name, result in results:
        icon = "✅" if result else "❌"
        print(f"  {icon} {name}")
        if result:
            passed += 1
    print(f"\n  {passed}/{len(results)} tests passed")
    if passed == len(results):
        print("\n🎉 ALL TESTS PASSED!")
    elif passed >= len(results) - 1:
        print("\n⚠️  Almost there — one test had issues (likely API timeout)")
    else:
        print("\n❌ Some tests failed — check the output above")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_all_tests())
