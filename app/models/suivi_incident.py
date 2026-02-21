from sqlalchemy import Column, Integer, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class SuiviIncident(Base):
    __tablename__ = "suiviincident"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dateSuivi = Column(Date, nullable=False)
    actionsPrises = Column(Text, nullable=False)
    idIncident = Column(Integer, ForeignKey("incident.id"), nullable=False)
    idMedecin = Column(Integer, ForeignKey("medecin.id"), nullable=True)

    incident = relationship("Incident", back_populates="suivis")