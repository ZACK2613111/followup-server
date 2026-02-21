from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.suivi_incident import SuiviCreate, SuiviResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/api/incidents", tags=["Suivis"])

@router.post("/{id}/suivis", response_model=SuiviResponse, status_code=status.HTTP_201_CREATED)
def add_suivi(id: int, data: SuiviCreate, db: Session = Depends(get_db)):
    """Ajouter un suivi à un incident"""
    suivi = IncidentService.add_suivi(db, id, data)
    if not suivi:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return suivi

@router.get("/{id}/suivis", response_model=List[SuiviResponse])
def get_suivis(id: int, db: Session = Depends(get_db)):
    """Historique des suivis d'un incident"""
    return IncidentService.get_suivis(db, id)