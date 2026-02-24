"""
Tests unitaires - Logique métier
Partie 2.2 - IEC 62304 Classe B
"""
import pytest
from app.services.incident_service import IncidentService
from app.models.incident import Incident, StatutEnum
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.suivi_incident import SuiviCreate


class TestIncidentServiceCreation:
    """Tests de la logique métier : création d'incident"""

    def test_creation_patient_existant(self, db, patient_en_db):
        """✅ Création réussie avec patient existant"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Son faible après calibration",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, data)
        assert incident.id is not None
        assert incident.id > 0

    def test_id_auto_incremente(self, db, patient_en_db):
        """✅ L'ID est bien auto-incrémenté"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Premier incident",
            idPatient=patient_en_db.id
        )
        inc1 = IncidentService.create(db, data)

        data.description = "Deuxième incident"
        inc2 = IncidentService.create(db, data)

        assert inc2.id > inc1.id

    def test_horodatage_auto(self, db, patient_en_db):
        """✅ dateCreation est renseignée automatiquement"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Critique",
            description="Panne totale",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, data)
        assert incident.dateCreation is not None

    def test_statut_defaut_ouvert(self, db, patient_en_db):
        """✅ Statut par défaut = Ouvert"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Modéré",
            description="Test statut défaut",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, data)
        assert incident.statut == StatutEnum.ouvert

    def test_creation_patient_inexistant(self, db):
        """❌ Erreur si patient n'existe pas"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Test patient inexistant",
            idPatient=99999
        )
        with pytest.raises(ValueError, match="Patient"):
            IncidentService.create(db, data)

    def test_soft_delete_flag(self, db, patient_en_db):
        """✅ Nouvel incident a deleted=0"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Test soft delete flag",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, data)
        assert incident.deleted == 0


class TestIncidentServiceLecture:
    """Tests de lecture d'incidents"""

    def test_get_par_id_existant(self, db, patient_en_db):
        """✅ Récupération d'un incident existant"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Test lecture",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        fetched = IncidentService.get_by_id(db, created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.description == "Test lecture"

    def test_get_par_id_inexistant(self, db):
        """❌ Retourne None pour ID inexistant"""
        result = IncidentService.get_by_id(db, 99999)
        assert result is None

    def test_get_par_patient(self, db, patient_en_db):
        """✅ Liste des incidents d'un patient"""
        for i in range(3):
            data = IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Mineur",
                description=f"Incident {i+1}",
                idPatient=patient_en_db.id
            )
            IncidentService.create(db, data)

        incidents = IncidentService.get_by_patient(db, patient_en_db.id)
        assert len(incidents) == 3

    def test_get_exclut_soft_deleted(self, db, patient_en_db):
        """✅ Les incidents soft-deletés ne sont pas retournés"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="A supprimer",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        IncidentService.soft_delete(db, created.id)

        result = IncidentService.get_by_id(db, created.id)
        assert result is None


class TestIncidentServiceMiseAJour:
    """Tests de mise à jour d'incident"""

    def test_update_statut(self, db, patient_en_db):
        """✅ Mise à jour du statut"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Test update",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        updated = IncidentService.update(db, created.id, IncidentUpdate(statut="Résolu"))
        assert updated.statut == StatutEnum.resolu

    def test_update_partiel(self, db, patient_en_db):
        """✅ Update partiel ne modifie pas les champs non fournis"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Description originale",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        IncidentService.update(db, created.id, IncidentUpdate(statut="EnCours"))

        fetched = IncidentService.get_by_id(db, created.id)
        assert fetched.description == "Description originale"
        assert fetched.gravite.value == "Mineur"

    def test_update_inexistant(self, db):
        """❌ Update retourne None si incident inexistant"""
        result = IncidentService.update(db, 99999, IncidentUpdate(statut="Résolu"))
        assert result is None


class TestIncidentServiceSuppression:
    """Tests de soft delete"""

    def test_soft_delete_succes(self, db, patient_en_db):
        """✅ Soft delete réussi"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="A supprimer",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        result = IncidentService.soft_delete(db, created.id)
        assert result is True

    def test_soft_delete_ne_supprime_pas_physiquement(self, db, patient_en_db):
        """✅ L'enregistrement reste en base avec deleted=1"""
        from app.models.incident import Incident
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Soft delete test",
            idPatient=patient_en_db.id
        )
        created = IncidentService.create(db, data)
        IncidentService.soft_delete(db, created.id)

        # Vérification directe en base (sans filtre deleted)
        raw = db.query(Incident).filter(Incident.id == created.id).first()
        assert raw is not None
        assert raw.deleted == 1

    def test_soft_delete_inexistant(self, db):
        """❌ Retourne False si incident inexistant"""
        result = IncidentService.soft_delete(db, 99999)
        assert result is False


class TestSuiviService:
    """Tests de la logique métier des suivis"""

    def test_ajout_suivi_incident_existant(self, db, patient_en_db):
        """✅ Ajout d'un suivi à un incident existant"""
        incident_data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Modéré",
            description="Processeur défectueux",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, incident_data)

        suivi_data = SuiviCreate(
            dateSuivi="2024-03-25",
            actionsPrises="Remplacement du processeur"
        )
        suivi = IncidentService.add_suivi(db, incident.id, suivi_data)
        assert suivi is not None
        assert suivi.idIncident == incident.id

    def test_ajout_suivi_incident_inexistant(self, db):
        """❌ Retourne None si incident inexistant"""
        suivi_data = SuiviCreate(
            dateSuivi="2024-03-25",
            actionsPrises="Action test"
        )
        result = IncidentService.add_suivi(db, 99999, suivi_data)
        assert result is None

    def test_historique_suivis(self, db, patient_en_db):
        """✅ Historique complet des suivis d'un incident"""
        incident_data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Majeur",
            description="Perte auditive",
            idPatient=patient_en_db.id
        )
        incident = IncidentService.create(db, incident_data)

        for i in range(3):
            IncidentService.add_suivi(db, incident.id, SuiviCreate(
                dateSuivi="2024-03-25",
                actionsPrises=f"Action {i+1}"
            ))

        suivis = IncidentService.get_suivis(db, incident.id)
        assert len(suivis) == 3