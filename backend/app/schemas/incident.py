from pydantic import BaseModel
from typing import Optional


class IncidentCreate(BaseModel):
    source: str
    description: str


class IncidentRead(BaseModel):
    id: int
    source: str
    description: str
    audio_path: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None
    risk_score: Optional[float] = None

    class Config:
        from_attributes = True
