# backend/scripts/seed_incidents.py
# Seeds the database with sample incident data for testing and development
#
# Usage:
#   cd backend
#   source ../.venv/bin/activate
#   PYTHONPATH=. python scripts/seed_incidents.py
#
# Day 51: Updated to include created_at timestamps so the TIME column works
#         in the frontend, and includes all fields matching current schema

# Import asyncio to run async database operations from synchronous code
import asyncio

# Import random for generating varied test data
import random

# Import datetime for creating realistic timestamps
from datetime import datetime, timedelta

# Import database connection and engine for table creation
from app.db.database import database, engine

# Import the incidents table definition and metadata
from app.db.models import incidents, metadata


# ========================================
# SAMPLE INCIDENT DATA
# ========================================

# Each incident has all the fields a real incident would have
# These cover all incident types and severity levels for thorough testing
SAMPLE_INCIDENTS = [
    {
        "source": "citizen",
        "description": "Large fire reported at 123 Main Street. Heavy smoke visible from highway. Multiple floors appear to be involved.",
        "location": "123 Main Street",
        "incident_type": "fire",
        "severity": "high",
        "risk_score": 0.95,
        "summary": "Major structure fire at 123 Main Street with heavy smoke. Multiple floors involved.",
    },
    {
        "source": "dispatcher",
        "description": "Multi-vehicle collision on Highway 101 northbound. Traffic backed up for miles. At least 3 vehicles involved.",
        "location": "Highway 101 NB, mile marker 42",
        "incident_type": "traffic",
        "severity": "medium",
        "risk_score": 0.72,
        "summary": "Multi-vehicle collision on Highway 101 causing major traffic backup.",
    },
    {
        "source": "citizen",
        "description": "Medical emergency - elderly person fell and cannot get up. Ambulance requested. Person is conscious but in pain.",
        "location": "456 Oak Avenue, Apartment 3B",
        "incident_type": "medical",
        "severity": "high",
        "risk_score": 0.88,
        "summary": "Elderly person fallen and unable to get up. Conscious but in pain. Ambulance needed.",
    },
    {
        "source": "citizen",
        "description": "Loud party noise complaint from neighbors. Music can be heard from street. This is the third complaint this week.",
        "location": "789 Elm Street",
        "incident_type": "noise",
        "severity": "low",
        "risk_score": 0.15,
        "summary": "Recurring noise complaint. Loud music audible from street. Third report this week.",
    },
    {
        "source": "sensor",
        "description": "Water main break detected. Street flooding reported. Water pressure dropping in surrounding blocks.",
        "location": "Corner of 5th Avenue and Cedar Road",
        "incident_type": "infrastructure",
        "severity": "medium",
        "risk_score": 0.65,
        "summary": "Water main break causing street flooding and pressure loss in surrounding area.",
    },
    {
        "source": "citizen",
        "description": "Suspicious person loitering near school playground after hours. Person appears to be watching children's area.",
        "location": "Lincoln Elementary School, 200 School Lane",
        "incident_type": "security",
        "severity": "medium",
        "risk_score": 0.58,
        "summary": "Suspicious individual observed near school playground after hours.",
    },
    {
        "source": "citizen",
        "description": "Minor fender bender in parking lot. No injuries. Drivers exchanging information. One car has a dented bumper.",
        "location": "Walmart parking lot, 500 Commerce Drive",
        "incident_type": "traffic",
        "severity": "low",
        "risk_score": 0.22,
        "summary": "Minor parking lot fender bender. No injuries. Drivers handling exchange.",
    },
    {
        "source": "dispatcher",
        "description": "Downed power line sparking on roadway. Area cordoned off by residents. Electric company has been notified.",
        "location": "400 block of Cedar Street",
        "incident_type": "infrastructure",
        "severity": "high",
        "risk_score": 0.91,
        "summary": "Downed power line sparking on road. Area cordoned off. Electric company notified.",
    },
    {
        "source": "citizen",
        "description": "Possible break-in at residence. Homeowner reports broken window and open door. No one appears to be inside currently.",
        "location": "567 Maple Drive",
        "incident_type": "crime",
        "severity": "high",
        "risk_score": 0.78,
        "summary": "Possible residential break-in. Broken window and open door reported. Scene appears clear.",
    },
    {
        "source": "sensor",
        "description": "Large pothole in road causing traffic hazard. Multiple cars swerving to avoid. Road surface deteriorating.",
        "location": "Broadway and 3rd Street intersection",
        "incident_type": "infrastructure",
        "severity": "medium",
        "risk_score": 0.45,
        "summary": "Hazardous pothole at intersection causing vehicles to swerve. Road deteriorating.",
    },
]


# ========================================
# SEED FUNCTION
# ========================================

async def seed_incidents():
    """
    Insert sample incidents into the database.
    Creates the tables if they don't exist, then inserts all sample data.
    """
    
    print("🌱 Seeding database with sample incidents...")
    
    # Create tables if they don't exist
    # This uses the sync engine because create_all is a synchronous operation
    metadata.create_all(engine)
    
    # Connect to the async database
    await database.connect()
    
    try:
        # Insert each sample incident
        for i, incident_data in enumerate(SAMPLE_INCIDENTS):
            
            # Generate a realistic created_at timestamp
            # Spread incidents over the past 7 days so the TIME column looks natural
            # Most recent incidents first (higher index = more recent)
            hours_ago = random.randint(1, 168)  # 1 hour to 7 days ago
            created_time = datetime.utcnow() - timedelta(hours=hours_ago)
            
            # Build the insert query with all fields
            query = incidents.insert().values(
                source=incident_data["source"],
                description=incident_data["description"],
                location=incident_data["location"],
                incident_type=incident_data["incident_type"],
                severity=incident_data["severity"],
                risk_score=incident_data["risk_score"],
                summary=incident_data["summary"],
                created_at=created_time,
                # These fields are null for seeded data (would be set by AI pipeline)
                audio_path=None,
                image_path=None,
                transcript=None,
                image_caption=None,
            )
            
            # Execute the insert and get the new ID
            incident_id = await database.execute(query)
            
            # Log each insertion
            print(f"  ✅ Inserted incident {i+1}/{len(SAMPLE_INCIDENTS)}: "
                  f"ID={incident_id} | {incident_data['incident_type']} | "
                  f"{created_time.strftime('%b %d %H:%M')}")
        
        print(f"\n🎉 Successfully seeded {len(SAMPLE_INCIDENTS)} incidents!")
        
    finally:
        # Always disconnect from the database when done
        await database.disconnect()


# ========================================
# ENTRY POINT
# ========================================

# Run the async seed function when this script is executed directly
if __name__ == "__main__":
    asyncio.run(seed_incidents())