"""
SuiviIncident model — tracks follow-up actions taken for a given incident.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class SuiviIncident(Base):
    __tablename__ = "suivis_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dateSuivi = Column(Date, nullable=False)
    actionsPrises = Column(Text, nullable=False)

    # Foreign keys
    idIncident = Column(Integer, ForeignKey("incidents.id"), nullable=False)
    idMedecin = Column(Integer, ForeignKey("medecins.id"), nullable=True)

    # Audit
    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    incident = relationship("Incident", back_populates="suivis")

    def __repr__(self):
        return f"<SuiviIncident id={self.id} idIncident={self.idIncident}>"