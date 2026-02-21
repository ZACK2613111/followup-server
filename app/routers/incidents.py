from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.services.incident_service import IncidentService

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])

@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    """Créer un nouvel incident"""
    try:
        return IncidentService.create(db, data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}", response_model=IncidentResponse)
def get_incident(id: int, db: Session = Depends(get_db)):
    """Récupérer un incident par ID"""
    incident = IncidentService.get_by_id(db, id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return incident

@router.put("/{id}", response_model=IncidentResponse)
def update_incident(id: int, data: IncidentUpdate, db: Session = Depends(get_db)):
    """Mettre à jour un incident"""
    incident = IncidentService.update(db, id, data)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident non trouvé")
    return incident

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_incident(id: int, db: Session = Depends(get_db)):
    """Supprimer un incident (soft delete)"""
    success = IncidentService.soft_delete(db, id)
    if not success:
        raise HTTPException(status_code=404, detail="Incident non trouvé")