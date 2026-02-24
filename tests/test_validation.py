"""
Tests unitaires - Validation des données
Partie 2.1 - IEC 62304 Classe B
"""
import pytest
from pydantic import ValidationError
from app.schemas.incident import IncidentCreate, IncidentUpdate
from app.schemas.suivi_incident import SuiviCreate


class TestIncidentCreateValidation:
    """Tests de validation du schéma IncidentCreate"""

    # ─── CAS NOMINAUX ───────────────────────────────────────────────────────

    def test_incident_valide_complet(self):
        """✅ Cas nominal : toutes les données valides"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Mineur",
            description="Son faible après calibration",
            idPatient=1,
            idImplant=1,
            idProcesseur=1,
            idMedecin=1
        )
        assert data.gravite == "Mineur"
        assert data.idPatient == 1

    def test_incident_valide_champs_optionnels_absents(self):
        """✅ Cas nominal : champs optionnels absents (implant, processeur, médecin)"""
        data = IncidentCreate(
            dateIncident="2024-03-20",
            heureIncident="14:30:00",
            gravite="Critique",
            description="Panne totale de l'implant",
            idPatient=2
        )
        assert data.idImplant is None
        assert data.idProcesseur is None
        assert data.idMedecin is None

    def test_toutes_les_gravites_valides(self):
        """✅ Cas nominal : chaque gravité acceptée"""
        for gravite in ["Mineur", "Modéré", "Majeur", "Critique"]:
            data = IncidentCreate(
                dateIncident="2024-01-01",
                heureIncident="10:00:00",
                gravite=gravite,
                description="Test gravité",
                idPatient=1
            )
            assert data.gravite == gravite

    def test_description_longueur_maximale(self):
        """✅ Cas nominal : description exactement 2000 caractères"""
        desc = "A" * 2000
        data = IncidentCreate(
            dateIncident="2024-01-01",
            heureIncident="10:00:00",
            gravite="Mineur",
            description=desc,
            idPatient=1
        )
        assert len(data.description) == 2000

    # ─── CAS D'ERREUR ───────────────────────────────────────────────────────

    def test_date_manquante(self):
        """❌ Erreur : dateIncident manquante"""
        with pytest.raises(ValidationError) as exc:
            IncidentCreate(
                heureIncident="14:30:00",
                gravite="Mineur",
                description="Test",
                idPatient=1
            )
        assert "dateIncident" in str(exc.value)

    def test_heure_manquante(self):
        """❌ Erreur : heureIncident manquante"""
        with pytest.raises(ValidationError) as exc:
            IncidentCreate(
                dateIncident="2024-03-20",
                gravite="Mineur",
                description="Test",
                idPatient=1
            )
        assert "heureIncident" in str(exc.value)

    def test_gravite_manquante(self):
        """❌ Erreur : gravite manquante"""
        with pytest.raises(ValidationError) as exc:
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                description="Test",
                idPatient=1
            )
        assert "gravite" in str(exc.value)

    def test_description_manquante(self):
        """❌ Erreur : description manquante"""
        with pytest.raises(ValidationError) as exc:
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Mineur",
                idPatient=1
            )
        assert "description" in str(exc.value)

    def test_patient_manquant(self):
        """❌ Erreur : idPatient manquant"""
        with pytest.raises(ValidationError) as exc:
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Mineur",
                description="Test"
            )
        assert "idPatient" in str(exc.value)

    def test_format_date_invalide(self):
        """❌ Erreur : format de date invalide"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="20/03/2024",  # format FR invalide
                heureIncident="14:30:00",
                gravite="Mineur",
                description="Test",
                idPatient=1
            )

    def test_format_date_texte(self):
        """❌ Erreur : date en texte libre"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="aujourd'hui",
                heureIncident="14:30:00",
                gravite="Mineur",
                description="Test",
                idPatient=1
            )

    def test_gravite_non_reconnue(self):
        """❌ Erreur : gravité non reconnue"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Catastrophique",  # valeur inconnue
                description="Test",
                idPatient=1
            )

    def test_gravite_casse_invalide(self):
        """❌ Erreur : gravité en minuscules (case sensitive)"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="mineur",  # doit être 'Mineur'
                description="Test",
                idPatient=1
            )

    def test_description_trop_longue(self):
        """❌ Erreur : description dépasse 2000 caractères"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Mineur",
                description="A" * 2001,
                idPatient=1
            )

    def test_patient_id_invalide(self):
        """❌ Erreur : idPatient non entier"""
        with pytest.raises(ValidationError):
            IncidentCreate(
                dateIncident="2024-03-20",
                heureIncident="14:30:00",
                gravite="Mineur",
                description="Test",
                idPatient="abc"
            )


class TestIncidentUpdateValidation:
    """Tests de validation du schéma IncidentUpdate"""

    def test_update_partiel_valide(self):
        """✅ Update partiel : seulement le statut"""
        data = IncidentUpdate(statut="Résolu")
        assert data.statut == "Résolu"
        assert data.gravite is None

    def test_update_statut_invalide(self):
        """❌ Statut inconnu"""
        with pytest.raises(ValidationError):
            IncidentUpdate(statut="Annulé")

    def test_update_vide_accepte(self):
        """✅ Update vide accepté (PATCH partiel)"""
        data = IncidentUpdate()
        assert data.statut is None
        assert data.gravite is None


class TestSuiviCreateValidation:
    """Tests de validation du schéma SuiviCreate"""

    def test_suivi_valide(self):
        """✅ Suivi valide"""
        data = SuiviCreate(
            dateSuivi="2024-03-25",
            actionsPrises="Recalibration du processeur effectuée"
        )
        assert data.actionsPrises == "Recalibration du processeur effectuée"

    def test_suivi_date_manquante(self):
        """❌ Date de suivi manquante"""
        with pytest.raises(ValidationError):
            SuiviCreate(actionsPrises="Ajustement effectué")

    def test_suivi_actions_manquantes(self):
        """❌ Actions prises manquantes"""
        with pytest.raises(ValidationError):
            SuiviCreate(dateSuivi="2024-03-25")