"""
Pydantic schemas for SuiviIncident — follow-up actions on an incident.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional


class SuiviCreate(BaseModel):
    """Schema for adding a follow-up to an incident."""
    dateSuivi: date = Field(..., description="Date du suivi (YYYY-MM-DD)")
    actionsPrises: str = Field(..., min_length=5, description="Description des actions prises")
    idMedecin: Optional[int] = Field(None, gt=0, description="ID du médecin ayant effectué le suivi")

    @field_validator("actionsPrises")
    @classmethod
    def actions_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Les actions prises ne peuvent pas être vides.")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "dateSuivi": "2024-03-25",
                "actionsPrises": "Ajustement du volume du processeur. Patient informé.",
                "idMedecin": 1
            }
        }
    }


class SuiviResponse(BaseModel):
    """Schema for follow-up responses."""
    id: int
    dateSuivi: date
    actionsPrises: str
    idIncident: int
    idMedecin: Optional[int] = None
    dateCreation: Optional[datetime] = None

    model_config = {"from_attributes": True}