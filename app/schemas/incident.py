"""
Pydantic schemas for Incident — request validation and response serialization.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date, time, datetime
from typing import Optional
from app.models.incident import GraviteEnum, StatutEnum


class IncidentCreate(BaseModel):
    """Schema for creating a new incident."""
    dateIncident: date = Field(..., description="Date de l'incident (YYYY-MM-DD)")
    heureIncident: time = Field(..., description="Heure de l'incident (HH:MM:SS)")
    gravite: GraviteEnum = Field(..., description="Niveau de gravité: Mineur, Modéré, Majeur, Critique")
    description: str = Field(..., min_length=5, max_length=2000, description="Description détaillée de l'incident")
    idPatient: int = Field(..., gt=0, description="ID du patient concerné")
    idImplant: Optional[int] = Field(None, gt=0, description="ID de l'implant concerné")
    idProcesseur: Optional[int] = Field(None, gt=0, description="ID du processeur concerné")
    idMedecin: Optional[int] = Field(None, gt=0, description="ID du médecin responsable")

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("La description ne peut pas être vide ou composée uniquement d'espaces.")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "dateIncident": "2024-03-20",
                "heureIncident": "14:30:00",
                "gravite": "Mineur",
                "description": "Son faible après calibration du processeur.",
                "idPatient": 1,
                "idImplant": 1,
                "idProcesseur": 1,
                "idMedecin": 1
            }
        }
    }


class IncidentUpdate(BaseModel):
    """Schema for partial update of an incident (PATCH-style via PUT)."""
    gravite: Optional[GraviteEnum] = Field(None, description="Nouveau niveau de gravité")
    description: Optional[str] = Field(None, min_length=5, max_length=2000)
    statut: Optional[StatutEnum] = Field(None, description="Nouveau statut")
    idMedecin: Optional[int] = Field(None, gt=0)

    @field_validator("description")
    @classmethod
    def description_not_empty(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("La description ne peut pas être vide.")
        return v.strip() if v else v


class IncidentResponse(BaseModel):
    """Schema for incident responses returned to clients."""
    id: int
    dateIncident: date
    heureIncident: time
    gravite: GraviteEnum
    description: str
    statut: StatutEnum
    idPatient: int
    idImplant: Optional[int] = None
    idProcesseur: Optional[int] = None
    idMedecin: Optional[int] = None
    dateCreation: Optional[datetime] = None
    dateModification: Optional[datetime] = None

    model_config = {"from_attributes": True}