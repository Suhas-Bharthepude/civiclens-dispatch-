# backend/scripts/seed_incidents.py
# This script seeds the database with fake incident data for testing
# Run this to populate your database with sample incidents

# Import asyncio for async operations
import asyncio

# Import database connection
from app.db.database import database, engine, metadata

# Import incidents table
from app.db.models import incidents


async def seed_incidents():
    """
    Insert sample incidents into the database.
    Useful for testing and development.
    """
    
    # Connect to database
    await database.connect()
    
    # Ensure tables exist
    metadata.create_all(engine)
    
    print("🌱 Seeding database with sample incidents...")
    
    # Sample incident data
    sample_incidents = [
        {
            "source": "citizen",
            "description": "Large fire reported at 123 Main Street. Heavy smoke visible from highway.",
            "location": "123 Main Street",
            "risk_score": 0.95,
            "incident_type": "fire",
            "severity": "high"
        },
        {
            "source": "police",
            "description": "Multi-vehicle collision on Highway 101 northbound. Traffic backed up for miles.",
            "location": "Highway 101 NB, mile marker 45",
            "risk_score": 0.72,
            "incident_type": "traffic",
            "severity": "medium"
        },
        {
            "source": "dispatcher",
            "description": "Medical emergency - elderly person fell and cannot get up. Ambulance requested.",
            "location": "456 Oak Avenue, Apt 3B",
            "risk_score": 0.88,
            "incident_type": "medical",
            "severity": "high"
        },
        {
            "source": "citizen",
            "description": "Loud party noise complaint from neighbors. Music can be heard from street.",
            "location": "789 Elm Street",
            "risk_score": 0.15,
            "incident_type": "noise",
            "severity": "low"
        },
        {
            "source": "sensor",
            "description": "Water main break detected. Street flooding reported.",
            "location": "Corner of 5th Ave and Pine St",
            "risk_score": 0.65,
            "incident_type": "infrastructure",
            "severity": "medium"
        },
        {
            "source": "citizen",
            "description": "Suspicious person loitering near school playground after hours.",
            "location": "Lincoln Elementary School, 321 School Road",
            "risk_score": 0.58,
            "incident_type": "security",
            "severity": "medium"
        },
        {
            "source": "police",
            "description": "Minor fender bender in parking lot. No injuries. Drivers exchanging information.",
            "location": "Walmart parking lot, 999 Commerce Blvd",
            "risk_score": 0.22,
            "incident_type": "traffic",
            "severity": "low"
        },
        {
            "source": "citizen",
            "description": "Downed power line sparking on roadway. Area cordoned off by residents.",
            "location": "400 block of Cedar Lane",
            "risk_score": 0.91,
            "incident_type": "infrastructure",
            "severity": "high"
        },
        {
            "source": "dispatcher",
            "description": "Possible break-in at residence. Homeowner reports broken window and open door.",
            "location": "567 Maple Drive",
            "risk_score": 0.78,
            "incident_type": "crime",
            "severity": "high"
        },
        {
            "source": "citizen",
            "description": "Large pothole in road causing traffic hazard. Multiple cars swerving to avoid.",
            "location": "Broadway and 3rd Street intersection",
            "risk_score": 0.45,
            "incident_type": "infrastructure",
            "severity": "medium"
        }
    ]
    
    # Insert each incident
    for idx, incident_data in enumerate(sample_incidents, 1):
        query = incidents.insert().values(**incident_data)
        incident_id = await database.execute(query)
        print(f"✅ Inserted incident {idx}/10: ID={incident_id} | {incident_data['incident_type']}")
    
    print(f"\n🎉 Successfully seeded {len(sample_incidents)} incidents!")
    
    # Disconnect from database
    await database.disconnect()


if __name__ == "__main__":
    """
    Run this script directly to seed the database:
    
    From project root:
        python -m backend.scripts.seed_incidents
    
    Or from backend directory:
        python -m scripts.seed_incidents
    """
    asyncio.run(seed_incidents())