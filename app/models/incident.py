from datetime import datetime
import enum
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum, SmallInteger
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

    # Sans ForeignKey — juste les IDs stockés
    idPatient = Column(Integer, nullable=False)
    idImplant = Column(Integer, nullable=True)
    idProcesseur = Column(Integer, nullable=True)
    idMedecin = Column(Integer, nullable=True)

    # Audit
    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)
    dateModification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = Column(SmallInteger, default=0, nullable=False)

    # Relationship
    suivis = relationship("SuiviIncident", back_populates="incident", cascade="all, delete-orphan")