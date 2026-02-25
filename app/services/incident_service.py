"""
IncidentService — business logic layer for incident management.

Handles all CRUD operations and follow-up management.
Validates business rules (patient existence, implant existence, etc.)
Conforms to IEC 62304 Class B software requirements.
"""

import logging
from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.incident import Incident, StatutEnum
from app.models.suivi_incident import SuiviIncident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.suivi_incident import SuiviCreate

logger = logging.getLogger(__name__)


class IncidentService:

    # ─────────────────────────────────────────────
    # INCIDENTS
    # ─────────────────────────────────────────────

    @staticmethod
    def create(db: Session, data: IncidentCreate) -> Incident:
        """
        Create a new incident after validating that the patient exists.
        Raises ValueError if patient not found.
        """
        from app.models.patient import Patient

        logger.info(f"Creating incident for patient {data.idPatient}")

        # Business rule: patient must exist
        patient = db.query(Patient).filter(Patient.id == data.idPatient).first()
        if not patient:
            logger.warning(f"Incident creation failed: patient {data.idPatient} not found")
            raise ValueError(f"Patient avec l'ID {data.idPatient} introuvable.")

        # Business rule: implant must belong to patient if provided
        if data.idImplant and patient.idImplant != data.idImplant:
            logger.warning(f"Implant {data.idImplant} does not belong to patient {data.idPatient}")
            raise ValueError(f"L'implant {data.idImplant} n'appartient pas au patient {data.idPatient}.")

        incident = Incident(**data.model_dump())
        db.add(incident)
        db.commit()
        db.refresh(incident)

        logger.info(f"Incident {incident.id} created successfully (gravite={incident.gravite})")
        return incident

    @staticmethod
    def get_by_id(db: Session, incident_id: int) -> Optional[Incident]:
        """
        Retrieve an active (non-deleted) incident by its ID.
        Returns None if not found or soft-deleted.
        """
        logger.debug(f"Fetching incident {incident_id}")
        return db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()

    @staticmethod
    def get_by_patient(db: Session, patient_id: int) -> List[Incident]:
        """
        Retrieve all active incidents for a given patient, ordered by date descending.
        """
        logger.debug(f"Fetching incidents for patient {patient_id}")
        return db.query(Incident).filter(
            Incident.idPatient == patient_id,
            Incident.deleted == 0
        ).order_by(Incident.dateIncident.desc(), Incident.heureIncident.desc()).all()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Incident]:
        """
        Retrieve all active incidents with pagination support.
        """
        logger.debug(f"Fetching all incidents (skip={skip}, limit={limit})")
        return db.query(Incident).filter(
            Incident.deleted == 0
        ).order_by(Incident.dateCreation.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, incident_id: int, data: IncidentUpdate) -> Optional[Incident]:
        """
        Partially update an incident. Only provided fields are updated.
        Returns None if incident not found or is soft-deleted.
        """
        logger.info(f"Updating incident {incident_id}")

        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()

        if not incident:
            logger.warning(f"Update failed: incident {incident_id} not found")
            return None

        updated_fields = data.model_dump(exclude_none=True)
        for field, value in updated_fields.items():
            setattr(incident, field, value)

        db.commit()
        db.refresh(incident)

        logger.info(f"Incident {incident_id} updated: {list(updated_fields.keys())}")
        return incident

    @staticmethod
    def soft_delete(db: Session, incident_id: int) -> bool:
        """
        Soft-delete an incident by setting deleted=1 and statut=Fermé.
        Returns False if incident not found or already deleted.
        """
        logger.info(f"Soft-deleting incident {incident_id}")

        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()

        if not incident:
            logger.warning(f"Soft-delete failed: incident {incident_id} not found")
            return False

        incident.deleted = 1
        incident.statut = StatutEnum.FERME
        db.commit()

        logger.info(f"Incident {incident_id} soft-deleted successfully")
        return True

    # ─────────────────────────────────────────────
    # SUIVIS
    # ─────────────────────────────────────────────

    @staticmethod
    def add_suivi(db: Session, incident_id: int, data: SuiviCreate) -> Optional[SuiviIncident]:
        """
        Add a follow-up action to an existing incident.
        Also transitions incident status to EnCours if it was Ouvert.
        Returns None if the incident is not found or is soft-deleted.
        """
        logger.info(f"Adding suivi to incident {incident_id}")

        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()

        if not incident:
            logger.warning(f"Add suivi failed: incident {incident_id} not found")
            return None

        # Business rule: auto-transition to EnCours when first suivi is added
        if incident.statut == StatutEnum.OUVERT:
            incident.statut = StatutEnum.EN_COURS
            logger.info(f"Incident {incident_id} status transitioned to EnCours")

        suivi = SuiviIncident(idIncident=incident_id, **data.model_dump())
        db.add(suivi)
        db.commit()
        db.refresh(suivi)

        logger.info(f"Suivi {suivi.id} added to incident {incident_id}")
        return suivi

    @staticmethod
    def get_suivis(db: Session, incident_id: int) -> List[SuiviIncident]:
        """
        Retrieve all follow-ups for a given incident, ordered by date ascending.
        """
        logger.debug(f"Fetching suivis for incident {incident_id}")
        return db.query(SuiviIncident).filter(
            SuiviIncident.idIncident == incident_id
        ).order_by(SuiviIncident.dateSuivi.asc()).all()