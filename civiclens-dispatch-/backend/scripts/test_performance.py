# backend/scripts/test_performance.py
# Performance test script that measures query speed
# Inserts many test incidents, runs common queries, and reports timing
#
# Usage:
#   Make sure backend server is running, then:
#   cd backend && source ../.venv/bin/activate
#   PYTHONPATH=. python scripts/test_performance.py
#
# Day 56: Database indexing and query performance testing

# Import httpx for making HTTP requests to our API
import httpx

# Import asyncio to run async functions
import asyncio

# Import time for measuring query durations
import time

# Import random for generating varied test data
import random


# ========================================
# CONFIGURATION
# ========================================

# Base URL of the running backend server
BASE_URL = "http://localhost:8000"

# Number of test incidents to create for performance testing
# More incidents = more realistic performance measurement
NUM_TEST_INCIDENTS = 50

# Request timeout in seconds
TIMEOUT = 30


# ========================================
# TEST DATA GENERATION
# ========================================

# Sample data for generating realistic test incidents
TYPES = ["fire", "medical", "traffic", "crime", "noise", "infrastructure", "other"]
SEVERITIES = ["high", "medium", "low"]
SOURCES = ["citizen", "dispatcher", "sensor"]
LOCATIONS = [
    "123 Main Street", "456 Oak Avenue", "789 Elm Street",
    "Highway 101 NB", "Downtown Plaza", "Industrial Boulevard",
    "School Lane", "Commerce Drive", "Cedar Road", "Park Avenue"
]
DESCRIPTIONS = [
    "Large fire reported with heavy smoke visible from highway",
    "Medical emergency - person collapsed on sidewalk",
    "Multi-vehicle collision with traffic backed up for miles",
    "Suspicious person loitering near school playground",
    "Loud noise complaint from residential area at night",
    "Water main break causing street flooding",
    "Minor fender bender in parking lot",
    "Downed power line sparking on roadway",
    "Possible break-in at residence with broken window",
    "Large pothole in road causing traffic hazard",
]


def generate_test_incident(index: int) -> dict:
    """
    Generate a random test incident for performance testing.
    
    Args:
        index: The incident number (used in description for uniqueness)
    
    Returns:
        Dict with source, description, and location fields
    """
    return {
        "source": random.choice(SOURCES),
        "description": f"[PERF TEST #{index}] {random.choice(DESCRIPTIONS)}",
        "location": random.choice(LOCATIONS),
    }


# ========================================
# PERFORMANCE TEST FUNCTIONS
# ========================================

async def measure_query(client: httpx.AsyncClient, name: str, url: str, params: dict = None) -> float:
    """
    Measure how long a single API query takes.
    
    Args:
        client: The HTTP client to use
        name: Human-readable name for the query
        url: The API URL to call
        params: Optional query parameters
    
    Returns:
        Duration in milliseconds
    """
    # Start the timer
    start = time.perf_counter()
    
    # Make the request
    response = await client.get(url, params=params)
    
    # Stop the timer
    duration_ms = (time.perf_counter() - start) * 1000
    
    # Get the number of results returned
    if response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else 1
    else:
        count = 0
    
    # Print the result
    print(f"  {name:40s} → {duration_ms:6.1f}ms ({count} results)")
    
    return duration_ms


async def run_performance_tests():
    """
    Run all performance tests:
    1. Create test incidents
    2. Time various query patterns
    3. Clean up test data
    """
    
    print("=" * 70)
    print("⚡ QUERY PERFORMANCE TESTS")
    print("=" * 70)
    print()
    
    # Track all created incident IDs for cleanup
    created_ids = []
    
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        
        # ── CHECK SERVER ──────────────────────────────
        try:
            r = await client.get(f"{BASE_URL}/health")
            if r.status_code != 200:
                print("❌ Server not responding. Start it first.")
                return
        except httpx.ConnectError:
            print("❌ Cannot connect to server. Start it with:")
            print("   uvicorn app.main:app --reload")
            return
        
        # ── COUNT EXISTING INCIDENTS ──────────────────
        r = await client.get(f"{BASE_URL}/incidents")
        existing_count = len(r.json())
        print(f"📊 Existing incidents in database: {existing_count}")
        
        # ── CREATE TEST INCIDENTS ─────────────────────
        print(f"\n📝 Creating {NUM_TEST_INCIDENTS} test incidents...")
        create_start = time.perf_counter()
        
        for i in range(NUM_TEST_INCIDENTS):
            incident = generate_test_incident(i + 1)
            r = await client.post(
                f"{BASE_URL}/incidents",
                json=incident
            )
            if r.status_code == 201:
                created_ids.append(r.json()["id"])
            
            # Print progress every 10 incidents
            if (i + 1) % 10 == 0:
                print(f"  Created {i + 1}/{NUM_TEST_INCIDENTS}...")
        
        create_time = time.perf_counter() - create_start
        print(f"  ✅ Created {len(created_ids)} incidents in {create_time:.1f}s")
        print(f"  📊 Total incidents now: {existing_count + len(created_ids)}")
        
        # ── RUN QUERY PERFORMANCE TESTS ───────────────
        total_incidents = existing_count + len(created_ids)
        print(f"\n🔍 Running query performance tests ({total_incidents} total incidents)...")
        print()
        
        # Test 1: Fetch all incidents (no filters)
        await measure_query(
            client, "All incidents (no filter)",
            f"{BASE_URL}/incidents"
        )
        
        # Test 2: Filter by incident type
        await measure_query(
            client, "Filter: type=fire",
            f"{BASE_URL}/incidents",
            params={"incident_type": "fire"}
        )
        
        # Test 3: Filter by severity
        await measure_query(
            client, "Filter: severity=high",
            f"{BASE_URL}/incidents",
            params={"severity": "high"}
        )
        
        # Test 4: Sort by risk score descending
        await measure_query(
            client, "Sort: risk_score DESC",
            f"{BASE_URL}/incidents",
            params={"sort_by": "risk_score", "sort_dir": "desc"}
        )
        
        # Test 5: Sort by created_at ascending
        await measure_query(
            client, "Sort: created_at ASC",
            f"{BASE_URL}/incidents",
            params={"sort_by": "created_at", "sort_dir": "asc"}
        )
        
        # Test 6: Search
        await measure_query(
            client, "Search: 'fire'",
            f"{BASE_URL}/incidents",
            params={"search": "fire"}
        )
        
        # Test 7: Combined filter + sort
        await measure_query(
            client, "Filter: severity=high + sort by risk",
            f"{BASE_URL}/incidents",
            params={"severity": "high", "sort_by": "risk_score", "sort_dir": "desc"}
        )
        
        # Test 8: Analytics summary (aggregate query)
        await measure_query(
            client, "Analytics summary",
            f"{BASE_URL}/analytics/summary"
        )
        
        # Test 9: AI status check
        await measure_query(
            client, "AI status check",
            f"{BASE_URL}/ai/status"
        )
        
        # Test 10: Single incident fetch
        if created_ids:
            await measure_query(
                client, f"Single incident (ID={created_ids[0]})",
                f"{BASE_URL}/incidents/{created_ids[0]}"
            )
        
        # ── CLEANUP ───────────────────────────────────
        print(f"\n🧹 Cleaning up {len(created_ids)} test incidents...")
        cleanup_start = time.perf_counter()
        
        for inc_id in created_ids:
            await client.delete(f"{BASE_URL}/incidents/{inc_id}")
        
        cleanup_time = time.perf_counter() - cleanup_start
        print(f"  ✅ Cleaned up in {cleanup_time:.1f}s")
        
        # ── SUMMARY ───────────────────────────────────
        print()
        print("=" * 70)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 70)
        print(f"  Total incidents tested: {total_incidents}")
        print(f"  Test incident creation: {create_time:.1f}s ({NUM_TEST_INCIDENTS} incidents)")
        print(f"  Cleanup time: {cleanup_time:.1f}s")
        print()
        print("  Indexes created on: incident_type, severity, risk_score, created_at")
        print("  These indexes speed up filtering and sorting operations.")
        print()
        print("  Note: With only ~60 incidents, query times are very fast.")
        print("  Indexes show their value at 1,000+ incidents.")
        print("  The important thing is that the infrastructure is in place.")
        print("=" * 70)


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    asyncio.run(run_performance_tests())