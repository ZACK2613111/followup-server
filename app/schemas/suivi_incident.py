from pydantic import BaseModel
from datetime import date
from typing import Optional

class SuiviCreate(BaseModel):
    dateSuivi: date
    actionsPrises: str
    idMedecin: Optional[int] = None

class SuiviResponse(BaseModel):
    id: int
    dateSuivi: date
    actionsPrises: str
    idIncident: int
    idMedecin: Optional[int]

    model_config = {"from_attributes": True}