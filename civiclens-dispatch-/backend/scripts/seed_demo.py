# backend/scripts/seed_demo.py
#
# Seeds the database with the 5 curated demo incidents from demo_data/sample_incidents.json
# Run this before any live demo or video recording to get a clean, predictable starting state.
#
# Usage:
#   cd backend
#   PYTHONPATH=. python scripts/seed_demo.py
#
# What it does:
#   1. Reads the 5 demo incidents from the JSON file
#   2. Posts each one to the running API (so the AI pipeline runs automatically)
#   3. Waits for all AI fields to populate
#   4. Prints a summary so you can confirm everything looks right before the demo
#
# IMPORTANT: The backend server must be running before you run this script.
#   cd backend && uvicorn app.main:app --reload

# Import httpx for making HTTP requests to our own API
import httpx

# Import asyncio to run async functions
import asyncio

# Import json to load the sample incidents file
import json

# Import time for polling and timing
import time

# Import Path to find the JSON file relative to this script
from pathlib import Path

# Import sys for exit codes
import sys


# ========================================
# CONFIGURATION
# ========================================

# Base URL of the running FastAPI server
BASE_URL = "http://localhost:8000"

# How long to wait for the AI pipeline to finish for each incident (seconds)
PIPELINE_TIMEOUT = 120

# How often to check if the pipeline is done (seconds)
POLL_INTERVAL = 3


# ========================================
# HELPER: WAIT FOR PIPELINE
# ========================================

async def wait_for_pipeline(client: httpx.AsyncClient, incident_id: int) -> dict:
    """
    Poll GET /incidents/{id} until all 4 AI fields are populated.
    Returns the final incident dict, or None if it times out.
    """

    # Record when we started waiting
    start = time.perf_counter()

    # Keep checking until we hit the timeout
    while time.perf_counter() - start < PIPELINE_TIMEOUT:

        # Fetch the current state of the incident
        response = await client.get(f"{BASE_URL}/incidents/{incident_id}")

        # If the fetch itself failed, something is wrong
        if response.status_code != 200:
            print(f"    ⚠️  Could not fetch incident #{incident_id}: {response.status_code}")
            return None

        # Parse the JSON response into a Python dict
        data = response.json()

        # Check if all 4 AI fields have been filled in by the pipeline
        if (
            data.get("incident_type") is not None and   # type was classified
            data.get("severity") is not None and         # severity was classified
            data.get("risk_score") is not None and       # risk score was calculated
            data.get("summary") is not None              # summary was generated
        ):
            # All fields populated — pipeline is done
            return data

        # Not done yet — show progress and wait
        elapsed = time.perf_counter() - start
        print(f"    ⏳ {elapsed:.0f}s — waiting for AI pipeline...")
        await asyncio.sleep(POLL_INTERVAL)

    # We hit the timeout without all fields being populated
    print(f"    ❌ Timed out waiting for pipeline on incident #{incident_id}")
    return None


# ========================================
# MAIN SEEDING FUNCTION
# ========================================

async def seed_demo():
    """
    Load demo incidents from JSON and post each one to the API.
    Wait for all AI fields to populate before moving to the next one.
    """

    print("=" * 60)
    print("🎬 DEMO DATA SEEDER")
    print("=" * 60)
    print(f"Server: {BASE_URL}")
    print()

    # ----------------------------------------
    # Step 1: Check the server is running
    # ----------------------------------------

    print("Checking server health...")

    try:
        # Quick health check before doing anything else
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{BASE_URL}/health")
            if resp.status_code != 200:
                print(f"❌ Server returned {resp.status_code} — is it running?")
                sys.exit(1)
    except httpx.ConnectError:
        # Can't connect at all — server isn't running
        print(f"❌ Cannot connect to {BASE_URL}")
        print("   Start the server first:")
        print("   cd backend && uvicorn app.main:app --reload")
        sys.exit(1)

    print("✅ Server is healthy\n")

    # ----------------------------------------
    # Step 2: Load the demo incidents from JSON
    # ----------------------------------------

    # Build the path to the JSON file relative to this script
    # Path(__file__) = this script file
    # .parent = the scripts/ folder
    # / "demo_data" / "..." = subfolder and filename
    json_path = Path(__file__).parent / "demo_data" / "sample_incidents.json"

    # Check the file exists
    if not json_path.exists():
        print(f"❌ Cannot find demo data file: {json_path}")
        print("   Make sure backend/scripts/demo_data/sample_incidents.json exists")
        sys.exit(1)

    # Load and parse the JSON file
    with open(json_path, "r") as f:
        demo_incidents = json.load(f)

    print(f"📋 Loaded {len(demo_incidents)} demo incidents from {json_path.name}\n")

    # ----------------------------------------
    # Step 3: Post each incident and wait for AI
    # ----------------------------------------

    # Track which incidents succeeded and which failed
    created = []  # list of (label, incident_id, final_data)
    failed = []   # list of (label, reason)

    # Use a single HTTP client for all requests
    async with httpx.AsyncClient(timeout=30) as client:

        # Loop through each demo incident
        for i, incident in enumerate(demo_incidents, start=1):

            # Extract the label and demo note for logging
            label = incident.get("label", f"Incident {i}")
            demo_note = incident.get("demo_note", "")

            print(f"--- {i}/{len(demo_incidents)}: {label} ---")

            # Build the API request body (only the fields the API expects)
            # Strip out our extra metadata fields like "label", "expected_type", etc.
            request_body = {
                "source": incident["source"],           # where the report came from
                "description": incident["description"], # the incident text
                "location": incident["location"],       # where it happened
            }

            # POST the incident to the API
            response = await client.post(
                f"{BASE_URL}/incidents",
                json=request_body
            )

            # Check if creation succeeded
            if response.status_code != 201:
                print(f"  ❌ Failed to create: {response.status_code} — {response.text[:100]}")
                failed.append((label, f"HTTP {response.status_code}"))
                print()
                continue  # Move to the next incident

            # Extract the new incident's ID from the response
            data = response.json()
            incident_id = data["id"]
            print(f"  ✅ Created incident #{incident_id}")

            # Wait for the AI pipeline to finish
            print(f"  🤖 Waiting for AI pipeline...")
            final_data = await wait_for_pipeline(client, incident_id)

            if final_data is None:
                # Pipeline timed out
                failed.append((label, "Pipeline timeout"))
                print()
                continue

            # Pipeline completed — show results
            risk_pct = int(final_data["risk_score"] * 100)
            print(f"  ✅ Pipeline complete!")
            print(f"     Type:     {final_data['incident_type']}")
            print(f"     Severity: {final_data['severity']}")
            print(f"     Risk:     {risk_pct}%")
            print(f"     Summary:  {final_data['summary'][:80]}...")

            # Check if the result matches what we expected
            expected_type = incident.get("expected_type")
            if expected_type and final_data["incident_type"] == expected_type:
                print(f"  ✅ Type matches expected '{expected_type}'")
            elif expected_type:
                print(f"  ⚠️  Type is '{final_data['incident_type']}', expected '{expected_type}'")

            # Save this incident's info for the summary
            created.append((label, incident_id, final_data))
            print()

    # ----------------------------------------
    # Step 4: Print the final summary
    # ----------------------------------------

    print("=" * 60)
    print("📊 DEMO SEED SUMMARY")
    print("=" * 60)
    print()

    if created:
        print(f"✅ {len(created)} incidents ready for demo:\n")
        for label, incident_id, data in created:
            # Print a clean one-line summary per incident
            risk_pct = int(data["risk_score"] * 100)
            print(f"  #{incident_id} [{data['severity'].upper()}] {data['incident_type']} — {risk_pct}% risk")
            print(f"     {label}")
            print()

    if failed:
        print(f"❌ {len(failed)} incidents failed:\n")
        for label, reason in failed:
            print(f"  • {label}: {reason}")
        print()

    if len(created) == len(demo_incidents):
        print("🎬 ALL DEMO INCIDENTS READY — you're good to go!")
    else:
        print(f"⚠️  Only {len(created)}/{len(demo_incidents)} incidents ready")

    print("=" * 60)


# ========================================
# ENTRY POINT
# ========================================

if __name__ == "__main__":
    # Run the async seed function
    asyncio.run(seed_demo())