from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Patient(Base):
    __tablename__ = "patient"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    dateNaissance = Column(Date, nullable=True)
    sexe = Column(String(20), nullable=True)
    adresse = Column(String(255), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)
    dateImplantation = Column(Date, nullable=True)
    idImplant = Column(Integer, nullable=True)