import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Enum, SmallInteger
from app.database import Base


class GraviteEnum(str, enum.Enum):
    MINEUR = "MINEUR"
    MODERE = "MODERE"
    MAJEUR = "MAJEUR"
    CRITIQUE = "CRITIQUE"


class StatutEnum(str, enum.Enum):
    OUVERT = "OUVERT"
    EN_COURS = "EN_COURS"
    RESOLU = "RESOLU"
    FERME = "FERME"


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dateIncident = Column(Date, nullable=False)
    heureIncident = Column(Time, nullable=False)
    gravite = Column(Enum(GraviteEnum), nullable=False)
    description = Column(String(2000), nullable=False)
    statut = Column(Enum(StatutEnum), default=StatutEnum.OUVERT, nullable=False)

    idPatient = Column(Integer, nullable=False)
    idImplant = Column(Integer, nullable=True)
    idProcesseur = Column(Integer, nullable=True)
    idMedecin = Column(Integer, nullable=True)

    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)
    dateModification = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    deleted = Column(SmallInteger, default=0, nullable=False)