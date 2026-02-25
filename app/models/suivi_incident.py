from datetime import datetime
from sqlalchemy import Column, Integer, Date, DateTime, Text
from app.database import Base


class SuiviIncident(Base):
    __tablename__ = "suivis_incidents"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dateSuivi = Column(Date, nullable=False)
    actionsPrises = Column(Text, nullable=False)

    idIncident = Column(Integer, nullable=False)
    idMedecin = Column(Integer, nullable=True)

    dateCreation = Column(DateTime, default=datetime.utcnow, nullable=False)