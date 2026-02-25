"""
FollowUp API — Entry point
CHU Montpellier - Gestion des incidents d'implants cochléaires
Version: 1.0.0
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import incidents, suivis, patients
from app.core.config import settings
from app.database import engine, Base

# ─────────────────────────────────────────────
# Logging configuration
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# App lifespan (startup / shutdown)
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown tasks."""
    logger.info("🚀 FollowUp API starting up...")
    # Create tables if they don't exist (dev convenience — use Alembic in prod)
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables verified.")
    yield
    logger.info("🛑 FollowUp API shutting down.")


# ─────────────────────────────────────────────
# FastAPI app
# ─────────────────────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "API REST pour la gestion des incidents d'implants cochléaires — CHU Montpellier.\n\n"
        "Conforme aux exigences IEC 62304 Classe B.\n\n"
        "**Endpoints principaux:**\n"
        "- `POST /api/incidents` — Déclarer un incident\n"
        "- `GET /api/incidents/{id}` — Détail d'un incident\n"
        "- `GET /api/patients/{id}/incidents` — Incidents d'un patient\n"
        "- `PUT /api/incidents/{id}` — Modifier un incident\n"
        "- `DELETE /api/incidents/{id}` — Supprimer (soft delete)\n"
        "- `POST /api/incidents/{id}/suivis` — Ajouter un suivi\n"
        "- `GET /api/incidents/{id}/suivis` — Historique des suivis\n"
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ─────────────────────────────────────────────
# CORS Middleware
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
# Global exception handler
# ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Une erreur interne est survenue. Veuillez contacter l'administrateur."}
    )

# ─────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────
app.include_router(incidents.router)
app.include_router(suivis.router)
app.include_router(patients.router)

# ─────────────────────────────────────────────
# Utility endpoints
# ─────────────────────────────────────────────
@app.get("/health", tags=["Health"], summary="Vérification de l'état du service")
def health_check():
    """Retourne le statut de l'API — utilisé par les health checks de Render."""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }