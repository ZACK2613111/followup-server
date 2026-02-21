from fastapi import FastAPI
from app.routers import incidents, suivis, patients

app = FastAPI(
    title="FollowUp API",
    description="API de gestion des incidents cochléaires - CHU Montpellier",
    version="1.0.0"
)

app.include_router(incidents.router)
app.include_router(suivis.router)
app.include_router(patients.router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "FollowUp API"}