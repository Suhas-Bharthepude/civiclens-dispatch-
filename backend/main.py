# This imports FastAPI, the tool that lets us create a web server
# FastAPI is the framework that lets us build APIs in Python
from fastapi import FastAPI

# BaseModel is the class we use to define data shapes
# Every request body model will inherit from it 
from pydantic import BaseModel


# You are defining a new data type
# It must follow rules from the imported BaseModel
class IncidentCreate(BaseModel):

    # Short description of what happened
    description: str

    # Location of the incident (text for now)
    location: str

    # Who submitted it (citizen, police, sensor, etc.)
    source: str
     
    # If any field is missing or wrong type, FastAPI automatically rejects the requests














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

def create_incident(incident: IncidentCreate):
    # 'incident: IncidentCreate' tells FastAPI to expect request body shaped like IncidentCreate 

    # FastAPI automatically
    # 1. Reads JSON from the request body
    # 2. Validates it against IncidentCreate
    # 3. Converts it into a Python object called 'incident'


    return {
        "id": 1,                 # Placeholder incident ID
        "status": "received",    # Initial status of the incident
        "priority": "unknown",    # Priority will be determined later by AI
        "description": incident.description,
        "location": incident.location,
        "source": incident.source


    }


    # test

    # return {
    #    "id": 1,                 # Placeholder incident ID
    #    "status": "received",    # Initial status of the incident
    #    "priority": "unknown",    # Priority will be determined later by AI
    #    "description": "Fire reported in apartment building",
    #    "location": "123 Main St",
    #    "source": "citizen"
    # }

    



    # If a client sends bad data:
    # The function never runs
    # FastAPI returns a clear error automatically












