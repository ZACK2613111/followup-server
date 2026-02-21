from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.suivi_incident import SuiviIncident
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.suivi_incident import SuiviCreate
from typing import List, Optional

class IncidentService:

    @staticmethod
    def create(db: Session, data: IncidentCreate) -> Incident:
        # Vérifie que le patient existe
        from app.models.patient import Patient
        patient = db.query(Patient).filter(Patient.id == data.idPatient).first()
        if not patient:
            raise ValueError(f"Patient {data.idPatient} introuvable")

        incident = Incident(**data.model_dump())
        db.add(incident)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def get_by_id(db: Session, incident_id: int) -> Optional[Incident]:
        return db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()

    @staticmethod
    def get_by_patient(db: Session, patient_id: int) -> List[Incident]:
        return db.query(Incident).filter(
            Incident.idPatient == patient_id,
            Incident.deleted == 0
        ).all()

    @staticmethod
    def update(db: Session, incident_id: int, data: IncidentUpdate) -> Optional[Incident]:
        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()
        if not incident:
            return None
        for key, value in data.model_dump(exclude_none=True).items():
            setattr(incident, key, value)
        db.commit()
        db.refresh(incident)
        return incident

    @staticmethod
    def soft_delete(db: Session, incident_id: int) -> bool:
        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()
        if not incident:
            return False
        incident.deleted = 1
        db.commit()
        return True

    @staticmethod
    def add_suivi(db: Session, incident_id: int, data: SuiviCreate) -> Optional[SuiviIncident]:
        incident = db.query(Incident).filter(
            Incident.id == incident_id,
            Incident.deleted == 0
        ).first()
        if not incident:
            return None
        suivi = SuiviIncident(idIncident=incident_id, **data.model_dump())
        db.add(suivi)
        db.commit()
        db.refresh(suivi)
        return suivi

    @staticmethod
    def get_suivis(db: Session, incident_id: int) -> List[SuiviIncident]:
        return db.query(SuiviIncident).filter(
            SuiviIncident.idIncident == incident_id
        ).all()