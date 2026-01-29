import asyncio
from app.db.database import database
from app.db.models import incidents


async def process_incident_async(incident_id: int):
    await asyncio.sleep(2)

    await database.execute(
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(
            transcript="Mock transcript",
            summary="Mock summary",
            risk_score=0.42
        )
    )
