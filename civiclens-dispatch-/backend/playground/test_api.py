# This file is used to test the API endpoints manually 
# It send HTTP requests to the FastAPI server 


# Import requests to send HTTP calls
import requests


# Base URL where FastAPI is running locally
BASE_URL = "http://127.0.0.1:8000"


# ----------------------------------------
# TEST: Create an incident
# ----------------------------------------


def post_incident():
    # Define a sample incident payload
    incident_data = {
        "description": "Test incident for Day 14",
        "location": "456 Sample Ave",
        "source": "test_api"
    }

    # Send POST request to create incident
    response = requests.post(
        f"{BASE_URL}/incidents",
        json=incident_data
    )

    # Print status code
    print("POST status:", response.status_code)

    # Print JSON response
    print("POST response:", response.json())



# ----------------------------------------
# TEST: List incidents with filters
# ----------------------------------------

def get_filtered_incidents():
    # Define query parameters
    params = {
        "source": "test_api",
        "limit": 5,
        "offset": 0,
        "sort_by": "id",
        "order": "desc"
    }

    # Send GET request with query params
    response = requests.get(
        f"{BASE_URL}/incidents",
        params=params
    )

    # Print status code
    print("\nGET status:", response.status_code)

    # Parse JSON response
    incidents = response.json()

    # Print number of incidents returned
    print(f"Returned {len(incidents)} incidents")

    # Print each incident
    for incident in incidents:
        print(
            f"ID={incident['id']} | "
            f"source={incident['source']} | "
            f"description={incident['description']}"
        )

     

if __name__ == "__main__":
    # Create an incident
    post_incident()
    
    # Fetch filtered & sorted incidents
    get_filtered_incidents()






