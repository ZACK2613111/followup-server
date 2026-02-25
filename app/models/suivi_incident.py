from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base


class SuiviIncident(Base):
    __tablename__ = "suivis_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dateSuivi = Column(Date, nullable=False)
    actionsPrises = Column(Text, nullable=False)

    # Sans ForeignKey
    idIncident = Column(Integer, nullable=False)
    idMedecin = Column(Integer, nullable=True)

    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)

    incident = relationship("Incident", back_populates="suivis",
                           foreign_keys="[SuiviIncident.idIncident]",
                           primaryjoin="SuiviIncident.idIncident == Incident.id")