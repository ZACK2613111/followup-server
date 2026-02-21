from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class GraviteEnum(str, enum.Enum):
    mineur = "Mineur"
    modere = "Modéré"
    majeur = "Majeur"
    critique = "Critique"

class StatutEnum(str, enum.Enum):
    ouvert = "Ouvert"
    en_cours = "EnCours"
    resolu = "Résolu"
    ferme = "Fermé"

class Incident(Base):
    __tablename__ = "incident"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dateIncident = Column(Date, nullable=False)
    heureIncident = Column(Time, nullable=False)
    gravite = Column(Enum(GraviteEnum), nullable=False)
    description = Column(String(2000), nullable=False)
    statut = Column(Enum(StatutEnum), default=StatutEnum.ouvert, nullable=False)
    idPatient = Column(Integer, ForeignKey("patient.id"), nullable=False)
    idImplant = Column(Integer, nullable=True)
    idProcesseur = Column(Integer, nullable=True)
    idMedecin = Column(Integer, ForeignKey("medecin.id"), nullable=True)
    dateCreation = Column(DateTime, server_default=func.now())
    dateModification = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted = Column(Integer, default=0)

    suivis = relationship("SuiviIncident", back_populates="incident")