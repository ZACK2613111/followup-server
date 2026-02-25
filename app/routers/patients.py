"""
Router: Patients
Handles patient-related queries, including their incident history.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.incident import IncidentResponse
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
    responses={
        404: {"description": "Patient non trouvé"},
    }
)


@router.get(
    "/{id}/incidents",
    response_model=List[IncidentResponse],
    summary="Incidents d'un patient",
    description="Retourne tous les incidents actifs d'un patient, ordonnés du plus récent au plus ancien."
)
def get_patient_incidents(id: int, db: Session = Depends(get_db)):
    """
    Récupère l'historique des incidents d'un patient.
    Vérifie d'abord que le patient existe.
    """
    from app.models.patient import Patient

    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        logger.warning(f"GET /api/patients/{id}/incidents → patient not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient {id} non trouvé.")

    incidents = IncidentService.get_by_patient(db, id)
    logger.info(f"GET /api/patients/{id}/incidents → returned {len(incidents)} incidents")
    return incidents