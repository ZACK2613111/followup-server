from sqlalchemy import Column, Integer, String
from app.database import Base

class Medecin(Base):
    __tablename__ = "medecin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    specialite = Column(String(100), nullable=True)
    telephone = Column(String(20), nullable=True)
    email = Column(String(150), nullable=True)