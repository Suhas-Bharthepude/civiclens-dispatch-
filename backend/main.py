# This imports FastAPI, the tool that lets us create a web server
# FastAPI is the framework that lets us build APIs in Python
from fastapi import FastAPI


# Routes is the URL pattern or path that maps to a specfic part of the application logic
# Endpoints are the specific functions or logic executed when a route is matched by an incoming HTTP request  

# This creates the instance of the FastAPI application 
# This application object represents our server
# All routes (endpoints) will be attached to this app

app = FastAPI()


# ----------------------------
# Root endpoint
# ----------------------------


# This decorator tell FastAPI that when someone sends a GET request to the URl '/', run the function below

@app.get("/")

def root(): 
    
    # This function runs when '/' is accessed in a browser or by a client 
    # FastAPI calls it when the route is hit
    # Returns a Python dictionary 
    


    return{
        "message": "CivicLens Dispatch API is running"
    }

    # FastAPI automatically converts this dictionary into JSON
    # Sends it back as the response
    # I did not write JSON manually as the FastAPI handles that
    # JSON is the standard format APIs use to send data


# ----------------------------
# List incidents endpoint
# ----------------------------


# This decorator means when someone sends a GET request to '/incidents', run this function
@app.get("/incidents")

def list_incidents():
    # This function represents a dispatcher asking "What incidents exist right now"
    # Right now we do NOT have a database connected so we return a empty list as a placeholder (called a stub)

    # "incidents" is a list that will eventually hold incident objects
    # "count" is the number of incidents in the system
    
    return {
        "incidents": [],
        "count": 0
    }



# ----------------------------
# Create incident endpoint
# ----------------------------

# This decorator means when someone sends a POST request to '/incidents', run this function"
# POST is used when creating new data

@app.post("/incidents")

def create_incident():
    # This function represents a citizen or system submitting a new incident 
    
    # In a real system, this function would:
    # 1. Validate incoming data 
    # 2. Save it to a database
    # 3. Assign a real ID
    # 4. Possibly run AI models 
    
    # For now, we return fake data to confirm the endpoint works 

    return {
        "id": 1,                 # Placeholder incident ID
        "status": "received",    # Initial status of the incident
        "priority": "unknown"    # Priority will be determined later by AI

    }

    








