import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db

# CRITIQUE : importer tous les models pour que SQLAlchemy les enregistre
from app.models.medecin import Medecin        # noqa
from app.models.patient import Patient         # noqa
from app.models.incident import Incident       # noqa
from app.models.suivi_incident import SuiviIncident  # noqa

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def patient_en_db(db):
    patient = Patient(
        nom="Dupont",
        prenom="Jean",
        email="jean.dupont@email.com",
        sexe="Masculin"
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@pytest.fixture
def incident_valide(patient_en_db):
    return {
        "dateIncident": "2024-03-20",
        "heureIncident": "14:30:00",
        "gravite": "Mineur",
        "description": "Son faible après calibration du processeur vocal",
        "idPatient": patient_en_db.id,
        "idMedecin": None
    }


@pytest.fixture
def incident_en_db(client, incident_valide):
    response = client.post("/api/incidents/", json=incident_valide)
    assert response.status_code == 201
    return response.json()