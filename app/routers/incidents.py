"""
Router: Incidents
Handles all CRUD operations on cochlear implant incidents.
Endpoints conform to TP06 specifications and IEC 62304 Class B requirements.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentResponse
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/incidents",
    tags=["Incidents"],
    responses={
        404: {"description": "Incident non trouvé"},
        400: {"description": "Données invalides"},
        500: {"description": "Erreur serveur interne"},
    }
)


@router.post(
    "/",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel incident",
    description="Déclare un nouvel incident lié à un implant cochléaire. Le patient doit exister."
)
def create_incident(data: IncidentCreate, db: Session = Depends(get_db)):
    """
    Crée un incident cochléaire.
    - Vérifie l'existence du patient
    - Vérifie la cohérence implant/patient si fourni
    - Statut initial: Ouvert
    """
    try:
        incident = IncidentService.create(db, data)
        logger.info(f"POST /api/incidents → created incident {incident.id}")
        return incident
    except ValueError as e:
        logger.warning(f"POST /api/incidents → validation error: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"POST /api/incidents → unexpected error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur interne du serveur.")


@router.get(
    "/",
    response_model=List[IncidentResponse],
    summary="Lister tous les incidents",
    description="Retourne tous les incidents actifs (non supprimés) avec pagination."
)
def list_incidents(
    skip: int = Query(0, ge=0, description="Nombre d'enregistrements à sauter"),
    limit: int = Query(100, ge=1, le=500, description="Nombre maximum de résultats"),
    db: Session = Depends(get_db)
):
    """Liste paginée de tous les incidents actifs."""
    incidents = IncidentService.get_all(db, skip=skip, limit=limit)
    logger.info(f"GET /api/incidents → returned {len(incidents)} incidents")
    return incidents


@router.get(
    "/{id}",
    response_model=IncidentResponse,
    summary="Récupérer un incident par ID",
    description="Retourne les détails d'un incident spécifique. Retourne 404 si non trouvé ou supprimé."
)
def get_incident(id: int, db: Session = Depends(get_db)):
    """Récupère un incident par son identifiant."""
    incident = IncidentService.get_by_id(db, id)
    if not incident:
        logger.warning(f"GET /api/incidents/{id} → not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {id} non trouvé.")
    return incident


@router.put(
    "/{id}",
    response_model=IncidentResponse,
    summary="Mettre à jour un incident",
    description="Met à jour les champs fournis d'un incident existant. Les champs non fournis sont conservés."
)
def update_incident(id: int, data: IncidentUpdate, db: Session = Depends(get_db)):
    """Mise à jour partielle d'un incident."""
    incident = IncidentService.update(db, id, data)
    if not incident:
        logger.warning(f"PUT /api/incidents/{id} → not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {id} non trouvé.")
    logger.info(f"PUT /api/incidents/{id} → updated")
    return incident


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un incident (soft delete)",
    description="Marque l'incident comme supprimé (deleted=1) et passe son statut à Fermé. Les données sont conservées."
)
def delete_incident(id: int, db: Session = Depends(get_db)):
    """Soft-delete d'un incident — les données sont conservées en base."""
    success = IncidentService.soft_delete(db, id)
    if not success:
        logger.warning(f"DELETE /api/incidents/{id} → not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Incident {id} non trouvé.")
    logger.info(f"DELETE /api/incidents/{id} → soft-deleted")