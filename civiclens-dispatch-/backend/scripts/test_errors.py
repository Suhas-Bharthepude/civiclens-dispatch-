# backend/scripts/test_errors.py
# Error handling test script
# Sends intentionally bad requests to verify the API handles them gracefully.
#
# Day 59: Original error handling tests
# Day 72: Updated to include a dispatcher auth token so body-validation
#          tests still receive 400/422 (not 401) on protected endpoints.
#
# Usage:
#   Make sure the backend server is running and seed_users.py has been run:
#     cd backend && source ../.venv/bin/activate
#     PYTHONPATH=. python scripts/test_errors.py

import httpx
import asyncio


BASE_URL = "http://localhost:8000"
TIMEOUT  = 10

# Dispatcher credentials created by scripts/seed_users.py
DISPATCHER_USERNAME = "dispatcher"
DISPATCHER_PASSWORD = "dispatch123"


# ========================================
# AUTH HELPER (Day 72)
# ========================================

async def _login(client: httpx.AsyncClient, username: str, password: str) -> dict:
    """Log in and return {Authorization: Bearer <token>}, or {} on failure."""
    try:
        r = await client.post(
            f"{BASE_URL}/auth/login",
            json={"username": username, "password": password},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            return {"Authorization": f"Bearer {r.json()['access_token']}"}
        print(f"  ⚠️  Login failed for '{username}': HTTP {r.status_code}")
        print(f"     Run: PYTHONPATH=. python scripts/seed_users.py")
        return {}
    except Exception as e:
        print(f"  ⚠️  Login request failed: {e}")
        return {}


async def get_dispatcher_headers(client: httpx.AsyncClient) -> dict:
    """Return auth headers for the dispatcher account."""
    return await _login(client, DISPATCHER_USERNAME, DISPATCHER_PASSWORD)


# ========================================
# TEST HELPER
# ========================================

async def test_request(
    client: httpx.AsyncClient,
    name: str,
    method: str,
    url: str,
    expected_status: int,
    json_data: dict = None,
    content: bytes = None,
    headers: dict = None,
) -> bool:
    """Send a request and check that the response matches the expected status."""
    print(f"\n  {name}")
    print(f"    {method} {url}")
    try:
        kwargs = {"timeout": TIMEOUT}
        if json_data  is not None: kwargs["json"]    = json_data
        if content    is not None: kwargs["content"]  = content
        if headers    is not None: kwargs["headers"]  = headers
        if method == "GET":
            response = await client.get(url, **kwargs)
        elif method == "POST":
            response = await client.post(url, **kwargs)
        elif method == "PATCH":
            response = await client.patch(url, **kwargs)
        elif method == "DELETE":
            response = await client.delete(url, **kwargs)
        else:
            print(f"    ❌ Unknown method: {method}")
            return False
        status_match = response.status_code == expected_status
        try:
            body = response.json()
            is_json = True
        except Exception:
            body = response.text[:200]
            is_json = False
        icon = "✅" if status_match else "❌"
        print(f"    {icon} Status: {response.status_code} (expected {expected_status})")
        if is_json and isinstance(body, dict):
            msg = body.get("message") or body.get("detail") or str(body)[:100]
            print(f"    📋 Response: {msg}")
        elif not is_json:
            print(f"    ⚠️  Response is not JSON: {body[:100]}")
        return status_match
    except Exception as e:
        print(f"    ❌ Request failed: {str(e)[:100]}")
        return False


# ========================================
# ALL ERROR TESTS
# ========================================

async def run_error_tests():
    """Run all error handling tests."""
    print("=" * 70)
    print("🛡️  ERROR HANDLING TESTS")
    print("=" * 70)
    print(f"Server: {BASE_URL}")

    results = []

    async with httpx.AsyncClient() as client:

        # Verify server is up
        try:
            r = await client.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code != 200:
                print("\n❌ Server not responding. Start it first.")
                return
        except httpx.ConnectError:
            print("\n❌ Cannot connect. Start the server first.")
            return

        # Obtain a dispatcher token so protected endpoints see the body
        # before checking auth — without this, all POST /incidents tests
        # would get 401 and never exercise Pydantic/business validation.
        auth_headers = await get_dispatcher_headers(client)
        if not auth_headers:
            print("\n⚠️  No auth token — run seed_users.py. Tests may fail with 401.")

        print("\n--- MISSING/INVALID DATA TESTS ---")

        # Test 1: Empty body
        results.append(await test_request(
            client, "Empty request body",
            "POST", f"{BASE_URL}/incidents",
            422,
            json_data={},
            headers=auth_headers,
        ))

        # Test 2: Missing description
        results.append(await test_request(
            client, "Missing description field",
            "POST", f"{BASE_URL}/incidents",
            422,
            json_data={"source": "citizen", "location": "123 Main St"},
            headers=auth_headers,
        ))

        # Test 3: Description too short
        results.append(await test_request(
            client, "Description too short (3 chars)",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "citizen", "description": "hi", "location": "123 Main St"},
            headers=auth_headers,
        ))

        # Test 4: All empty strings
        results.append(await test_request(
            client, "All empty strings",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "", "description": "", "location": ""},
            headers=auth_headers,
        ))

        # Test 5: Whitespace-only description
        results.append(await test_request(
            client, "Whitespace-only description",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "citizen", "description": "   ", "location": "123 Main St"},
            headers=auth_headers,
        ))

        # Test 6: Invalid source value
        results.append(await test_request(
            client, "Invalid source value",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "hacker", "description": "Valid description here", "location": "123 Main St"},
            headers=auth_headers,
        ))

        print("\n--- NOT FOUND TESTS ---")

        # Test 7: Non-existent incident
        results.append(await test_request(
            client, "Get incident that doesn't exist",
            "GET", f"{BASE_URL}/incidents/99999",
            404,
            headers=auth_headers,
        ))

        # Test 8: Update non-existent incident
        results.append(await test_request(
            client, "Update incident that doesn't exist",
            "PATCH", f"{BASE_URL}/incidents/99999",
            404,
            json_data={"severity": "high"},
            headers=auth_headers,
        ))

        # Test 9: Delete non-existent incident — admin token required (Day 72)
        admin_headers = await _login(client, "admin", "admin123")
        results.append(await test_request(
            client, "Delete incident that doesn't exist",
            "DELETE", f"{BASE_URL}/incidents/99999",
            404,
            headers=admin_headers,
        ))

        # Test 10: Reprocess non-existent incident
        results.append(await test_request(
            client, "Reprocess incident that doesn't exist",
            "POST", f"{BASE_URL}/incidents/99999/reprocess",
            404,
            headers=auth_headers,
        ))

        print("\n--- INVALID INPUT TYPE TESTS ---")

        # Test 11: String ID in URL
        results.append(await test_request(
            client, "String ID in URL (not a number)",
            "GET", f"{BASE_URL}/incidents/abc",
            422,
            headers=auth_headers,
        ))

        # Test 12: Non-JSON body
        results.append(await test_request(
            client, "Non-JSON request body",
            "POST", f"{BASE_URL}/incidents",
            422,
            content=b"this is not json",
            headers={**auth_headers, "Content-Type": "application/json"},
        ))

        print("\n--- VALID ENDPOINT TESTS (should succeed) ---")

        # Test 13: Valid incident creation
        results.append(await test_request(
            client, "Valid incident creation (should succeed)",
            "POST", f"{BASE_URL}/incidents",
            201,
            json_data={
                "source":      "citizen",
                "description": "This is a valid test incident for error handling verification",
                "location":    "123 Test Street",
            },
            headers=auth_headers,
        ))

        # Test 14: Health check (no auth required)
        results.append(await test_request(
            client, "Health check (always 200)",
            "GET", f"{BASE_URL}/health",
            200,
        ))

        # Cleanup the valid test incident — delete needs admin (Day 72)
        r = await client.get(f"{BASE_URL}/incidents", headers=auth_headers)
        if r.status_code == 200:
            final_admin = await _login(client, "admin", "admin123")
            for inc in r.json():
                if "error handling verification" in (inc.get("description") or ""):
                    await client.delete(
                        f"{BASE_URL}/incidents/{inc['id']}",
                        headers=final_admin,
                    )
                    print(f"\n  🧹 Cleaned up test incident #{inc['id']}")

    # Summary
    print("\n" + "=" * 70)
    print("📊 ERROR HANDLING TEST RESULTS")
    print("=" * 70)
    passed = sum(1 for r in results if r)
    for i, result in enumerate(results, 1):
        print(f"  {'✅' if result else '❌'} Test {i}")
    print(f"\n  {passed}/{len(results)} tests passed")
    if passed == len(results):
        print("\n🎉 ALL ERROR HANDLING TESTS PASSED!")
    elif passed >= len(results) - 2:
        print("\n⚠️  Almost perfect — check failed tests above")
    else:
        print("\n❌ Several tests failed — error handling needs work")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_error_tests())
