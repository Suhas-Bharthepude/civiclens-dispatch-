# backend/app/tasks/incident_tasks.py
# DEPRECATED: This file is no longer used.
# 
# Background task processing has been moved to:
# app/services/incident_processor.py
# 
# This file is kept for reference but will be removed in Day 22.
# 
# Historical note: This was an early attempt at background tasks
# before we consolidated everything into incident_processor.py

import asyncio
from app.db.database import database
from app.db.models import incidents


async def process_incident_async(incident_id: int):
    """
    DEPRECATED: Use app.services.incident_processor.process_incident instead.
    
    This function is no longer called.
    Kept for reference during Day 21 cleanup.
    """
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