import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

# Sample incident data
incident_data = {
    "title": "Test Incident",
    "description": "This is a test incident for Day 12 validation.",
    "location": "123 Test St, Test City",
    "risk_score": 5.0,
    "transcript": "Test transcript data",
    "summary": "Test summary",
    "source": "test_api"
}

def post_incident():
    try:
        response = requests.post(f"{BASE_URL}/incidents", json=incident_data)
        response.raise_for_status()
        print("✅ POST succeeded:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print("❌ POST request failed:", e)
        sys.exit(1)

def get_incidents():
    try:
        response = requests.get(f"{BASE_URL}/incidents")
        response.raise_for_status()
        incidents = response.json()
        print(f"\n📋 GET all incidents ({len(incidents)} found):")
        for i, incident in enumerate(incidents, start=1):
            print(f"{i}. {incident['description']} | {incident.get('source','N/A')} | ID: {incident['id']}")
    except requests.exceptions.RequestException as e:
        print("❌ GET request failed:", e)
        sys.exit(1)

if __name__ == "__main__":
    post_incident()
    get_incidents()
