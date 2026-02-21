from pydantic import BaseModel, Field
from datetime import date, time, datetime
from typing import Optional
from app.models.incident import GraviteEnum, StatutEnum

class IncidentCreate(BaseModel):
    dateIncident: date
    heureIncident: time
    gravite: GraviteEnum
    description: str = Field(..., max_length=2000)
    idPatient: int
    idImplant: Optional[int] = None
    idProcesseur: Optional[int] = None
    idMedecin: Optional[int] = None

class IncidentUpdate(BaseModel):
    gravite: Optional[GraviteEnum] = None
    description: Optional[str] = Field(None, max_length=2000)
    statut: Optional[StatutEnum] = None
    idMedecin: Optional[int] = None

class IncidentResponse(BaseModel):
    id: int
    dateIncident: date
    heureIncident: time
    gravite: GraviteEnum
    description: str
    statut: StatutEnum
    idPatient: int
    idMedecin: Optional[int]
    dateCreation: Optional[datetime]

    model_config = {"from_attributes": True}