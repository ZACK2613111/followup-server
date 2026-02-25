"""
Incident model — represents a cochlear implant incident reported by a patient.
Conforms to IEC 62304 Class B software classification.
"""

import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum, Text, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class GraviteEnum(str, enum.Enum):
    MINEUR = "Mineur"
    MODERE = "Modéré"
    MAJEUR = "Majeur"
    CRITIQUE = "Critique"


class StatutEnum(str, enum.Enum):
    OUVERT = "Ouvert"
    EN_COURS = "EnCours"
    RESOLU = "Résolu"
    FERME = "Fermé"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dateIncident = Column(Date, nullable=False)
    heureIncident = Column(Time, nullable=False)
    gravite = Column(Enum(GraviteEnum), nullable=False)
    description = Column(String(2000), nullable=False)
    statut = Column(Enum(StatutEnum), default=StatutEnum.OUVERT, nullable=False)

    # Foreign keys
    idPatient = Column(Integer, ForeignKey("patients.id"), nullable=False)
    idImplant = Column(Integer, ForeignKey("implants.id"), nullable=True)
    idProcesseur = Column(Integer, ForeignKey("processeurs.id"), nullable=True)
    idMedecin = Column(Integer, ForeignKey("medecins.id"), nullable=True)

    # Audit fields
    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)
    dateModification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = Column(SmallInteger, default=0, nullable=False)  # 0=active, 1=soft-deleted

    # Relationships
    suivis = relationship("SuiviIncident", back_populates="incident", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Incident id={self.id} gravite={self.gravite} statut={self.statut}>"