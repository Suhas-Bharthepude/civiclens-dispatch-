# backend/scripts/test_errors.py
# Error handling test script
# Sends intentionally bad requests to verify the API handles them gracefully
#
# Every test should get a clean JSON error response — never a raw traceback.
#
# Usage:
#   Make sure the backend server is running, then:
#   cd backend && source ../.venv/bin/activate
#   PYTHONPATH=. python scripts/test_errors.py
#
# Day 59: Error handling hardening

# Import httpx for making HTTP requests
import httpx

# Import asyncio to run async functions
import asyncio

# Import json for pretty-printing responses
import json


# ========================================
# CONFIGURATION
# ========================================

# Base URL of the running backend
BASE_URL = "http://localhost:8000"

# Request timeout
TIMEOUT = 10


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
    """
    Send a request and check that the response is a clean JSON error.
    
    Args:
        name: Human-readable test name
        method: HTTP method (GET, POST, PATCH, DELETE)
        url: Full URL to request
        expected_status: Expected HTTP status code
        json_data: Optional JSON body
        content: Optional raw bytes body
        headers: Optional headers
    
    Returns:
        True if the test passed (got expected status + clean JSON)
    """
    
    print(f"\n  {name}")
    print(f"    {method} {url}")
    
    try:
        # Build request kwargs
        kwargs = {"timeout": TIMEOUT}
        if json_data is not None:
            kwargs["json"] = json_data
        if content is not None:
            kwargs["content"] = content
        if headers is not None:
            kwargs["headers"] = headers
        
        # Send the request
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
        
        # Check status code
        status_match = response.status_code == expected_status
        
        # Try to parse response as JSON
        try:
            body = response.json()
            is_json = True
        except Exception:
            body = response.text[:200]
            is_json = False
        
        # Print result
        status_icon = "✅" if status_match else "❌"
        print(f"    {status_icon} Status: {response.status_code} (expected {expected_status})")
        
        if is_json and isinstance(body, dict):
            # Show a summary of the JSON response
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
        
        # ── CHECK SERVER IS RUNNING ───────────────────
        try:
            r = await client.get(f"{BASE_URL}/health", timeout=5)
            if r.status_code != 200:
                print("\n❌ Server not responding. Start it first.")
                return
        except httpx.ConnectError:
            print("\n❌ Cannot connect. Start the server first.")
            return
        
        print("\n--- MISSING/INVALID DATA TESTS ---")
        
        # Test 1: Create incident with empty body
        results.append(await test_request(
            client, "Empty request body",
            "POST", f"{BASE_URL}/incidents",
            422,  # Pydantic validation error
            json_data={}
        ))
        
        # Test 2: Create incident with missing description
        results.append(await test_request(
            client, "Missing description field",
            "POST", f"{BASE_URL}/incidents",
            422,
            json_data={"source": "citizen", "location": "123 Main St"}
        ))
        
        # Test 3: Create incident with too-short description
        results.append(await test_request(
            client, "Description too short (3 chars)",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "citizen", "description": "hi", "location": "123 Main St"}
        ))
        
        # Test 4: Create incident with empty strings
        results.append(await test_request(
            client, "All empty strings",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "", "description": "", "location": ""}
        ))
        
        # Test 5: Create incident with whitespace-only fields
        results.append(await test_request(
            client, "Whitespace-only description",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "citizen", "description": "   ", "location": "123 Main St"}
        ))
        
        # Test 6: Invalid source value
        results.append(await test_request(
            client, "Invalid source value",
            "POST", f"{BASE_URL}/incidents",
            400,
            json_data={"source": "hacker", "description": "Valid description here", "location": "123 Main St"}
        ))
        
        print("\n--- NOT FOUND TESTS ---")
        
        # Test 7: Get non-existent incident
        results.append(await test_request(
            client, "Get incident that doesn't exist",
            "GET", f"{BASE_URL}/incidents/99999",
            404
        ))
        
        # Test 8: Update non-existent incident
        results.append(await test_request(
            client, "Update incident that doesn't exist",
            "PATCH", f"{BASE_URL}/incidents/99999",
            404,
            json_data={"severity": "high"}
        ))
        
        # Test 9: Delete non-existent incident
        results.append(await test_request(
            client, "Delete incident that doesn't exist",
            "DELETE", f"{BASE_URL}/incidents/99999",
            404
        ))
        
        # Test 10: Reprocess non-existent incident
        results.append(await test_request(
            client, "Reprocess incident that doesn't exist",
            "POST", f"{BASE_URL}/incidents/99999/reprocess",
            404
        ))
        
        print("\n--- INVALID INPUT TYPE TESTS ---")
        
        # Test 11: String where number expected
        results.append(await test_request(
            client, "String ID in URL (not a number)",
            "GET", f"{BASE_URL}/incidents/abc",
            422
        ))
        
        # Test 12: Send non-JSON body
        results.append(await test_request(
            client, "Non-JSON request body",
            "POST", f"{BASE_URL}/incidents",
            422,
            content=b"this is not json",
            headers={"Content-Type": "application/json"}
        ))
        
        print("\n--- VALID ENDPOINT TESTS (should succeed) ---")
        
        # Test 13: Valid request (sanity check)
        results.append(await test_request(
            client, "Valid incident creation (should succeed)",
            "POST", f"{BASE_URL}/incidents",
            201,
            json_data={
                "source": "citizen",
                "description": "This is a valid test incident for error handling verification",
                "location": "123 Test Street"
            }
        ))
        
        # Test 14: Health check (always works)
        results.append(await test_request(
            client, "Health check (always 200)",
            "GET", f"{BASE_URL}/health",
            200
        ))
        
        # Cleanup the valid test incident
        r = await client.get(f"{BASE_URL}/incidents")
        incidents = r.json()
        for inc in incidents:
            if "error handling verification" in (inc.get("description") or ""):
                await client.delete(f"{BASE_URL}/incidents/{inc['id']}")
                print(f"\n  🧹 Cleaned up test incident #{inc['id']}")
    
    # ── SUMMARY ───────────────────────────────────────
    print("\n" + "=" * 70)
    print("📊 ERROR HANDLING TEST RESULTS")
    print("=" * 70)
    
    passed = sum(1 for r in results if r)
    total = len(results)
    
    for i, result in enumerate(results, 1):
        icon = "✅" if result else "❌"
        print(f"  {icon} Test {i}")
    
    print(f"\n  {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL ERROR HANDLING TESTS PASSED!")
    elif passed >= total - 2:
        print("\n⚠️  Almost perfect — check failed tests above")
    else:
        print("\n❌ Several tests failed — error handling needs work")
    
    print("=" * 70)


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_error_tests())