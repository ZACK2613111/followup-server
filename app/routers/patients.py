from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.incident import IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/{id}/incidents", response_model=List[IncidentResponse])
def get_patient_incidents(id: int, db: Session = Depends(get_db)):
    """Liste des incidents d'un patient"""
    return IncidentService.get_by_patient(db, id)