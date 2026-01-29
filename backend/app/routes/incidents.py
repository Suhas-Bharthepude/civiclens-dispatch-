from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from app.db.database import database
from app.db.models import incidents
from app.schemas.incident import IncidentCreate, IncidentRead
from app.utils.file_utils import save_upload_file
from app.tasks.incident_tasks import process_incident_async

router = APIRouter()


@router.post("/incidents", response_model=IncidentRead)
async def create_incident(
    incident: IncidentCreate,
    background_tasks: BackgroundTasks
):
    query = incidents.insert().values(
        source=incident.source,
        description=incident.description,
        audio_path=None,
        transcript=None,
        summary=None,
        risk_score=None
    )

    incident_id = await database.execute(query)

    background_tasks.add_task(process_incident_async, incident_id)

    return {
        "id": incident_id,
        "source": incident.source,
        "description": incident.description,
        "audio_path": None,
        "transcript": None,
        "summary": None,
        "risk_score": None,
    }


@router.get("/incidents", response_model=list[IncidentRead])
async def list_incidents():
    query = incidents.select()
    return await database.fetch_all(query)


@router.post("/incidents/{incident_id}/audio")
async def upload_audio(
    incident_id: int,
    file: UploadFile = File(...)
):
    file_path = save_upload_file(file, folder="audio")

    result = await database.execute(
        incidents
        .update()
        .where(incidents.c.id == incident_id)
        .values(audio_path=file_path)
    )

    if result is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    return {"audio_path": file_path}
