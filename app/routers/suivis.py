"""
Router: Suivis d'incidents
Handles follow-up actions on cochlear implant incidents.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.suivi_incident import SuiviCreate, SuiviResponse
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/incidents",
    tags=["Suivis d'incidents"],
    responses={
        404: {"description": "Incident non trouvé"},
        400: {"description": "Données invalides"},
    }
)


@router.post(
    "/{id}/suivis",
    response_model=SuiviResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ajouter un suivi à un incident",
    description=(
        "Ajoute une action de suivi à un incident existant. "
        "Si l'incident est en statut Ouvert, il passe automatiquement à EnCours."
    )
)
def add_suivi(id: int, data: SuiviCreate, db: Session = Depends(get_db)):
    """Crée un suivi pour l'incident spécifié."""
    suivi = IncidentService.add_suivi(db, id, data)
    if not suivi:
        logger.warning(f"POST /api/incidents/{id}/suivis → incident not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {id} non trouvé.")
    logger.info(f"POST /api/incidents/{id}/suivis → created suivi {suivi.id}")
    return suivi


@router.get(
    "/{id}/suivis",
    response_model=List[SuiviResponse],
    summary="Historique des suivis d'un incident",
    description="Retourne tous les suivis d'un incident, ordonnés par date croissante."
)
def get_suivis(id: int, db: Session = Depends(get_db)):
    """Récupère l'historique complet des suivis pour un incident."""
    # Verify the incident exists first
    incident = IncidentService.get_by_id(db, id)
    if not incident:
        logger.warning(f"GET /api/incidents/{id}/suivis → incident not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {id} non trouvé.")

    suivis = IncidentService.get_suivis(db, id)
    logger.info(f"GET /api/incidents/{id}/suivis → returned {len(suivis)} suivis")
    return suivis