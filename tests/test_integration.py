"""
Tests d'intégration - API REST
Partie 2.3 - IEC 62304 Classe B
"""
import pytest


class TestPostIncident:
    """Tests POST /api/incidents/"""

    def test_post_incident_valide(self, client, incident_valide):
        """✅ Création incident avec données valides → 201"""
        response = client.post("/api/incidents/", json=incident_valide)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["gravite"] == "Mineur"
        assert data["statut"] == "Ouvert"
        assert data["idPatient"] == incident_valide["idPatient"]

    def test_post_incident_champs_manquants(self, client, patient_en_db):
        """❌ Données incomplètes → 422"""
        response = client.post("/api/incidents/", json={
            "dateIncident": "2024-03-20"
            # tous les autres champs manquants
        })
        assert response.status_code == 422

    def test_post_incident_gravite_invalide(self, client, patient_en_db):
        """❌ Gravité non reconnue → 422"""
        response = client.post("/api/incidents/", json={
            "dateIncident": "2024-03-20",
            "heureIncident": "14:30:00",
            "gravite": "Catastrophique",
            "description": "Test",
            "idPatient": patient_en_db.id
        })
        assert response.status_code == 422

    def test_post_incident_patient_inexistant(self, client):
        """❌ Patient inexistant → 400"""
        response = client.post("/api/incidents/", json={
            "dateIncident": "2024-03-20",
            "heureIncident": "14:30:00",
            "gravite": "Mineur",
            "description": "Test patient inexistant",
            "idPatient": 99999
        })
        assert response.status_code == 400

    def test_post_incident_date_invalide(self, client, patient_en_db):
        """❌ Format date invalide → 422"""
        response = client.post("/api/incidents/", json={
            "dateIncident": "20/03/2024",
            "heureIncident": "14:30:00",
            "gravite": "Mineur",
            "description": "Test",
            "idPatient": patient_en_db.id
        })
        assert response.status_code == 422

    def test_post_incident_description_trop_longue(self, client, patient_en_db):
        """❌ Description > 2000 chars → 422"""
        response = client.post("/api/incidents/", json={
            "dateIncident": "2024-03-20",
            "heureIncident": "14:30:00",
            "gravite": "Mineur",
            "description": "A" * 2001,
            "idPatient": patient_en_db.id
        })
        assert response.status_code == 422

    def test_post_retourne_id_auto(self, client, incident_valide):
        """✅ L'ID retourné est automatiquement assigné"""
        r1 = client.post("/api/incidents/", json=incident_valide)
        incident_valide["description"] = "Deuxième incident différent"
        r2 = client.post("/api/incidents/", json=incident_valide)
        assert r2.json()["id"] > r1.json()["id"]

    def test_post_tous_niveaux_gravite(self, client, patient_en_db):
        """✅ Les 4 niveaux de gravité sont acceptés"""
        for gravite in ["Mineur", "Modéré", "Majeur", "Critique"]:
            response = client.post("/api/incidents/", json={
                "dateIncident": "2024-03-20",
                "heureIncident": "14:30:00",
                "gravite": gravite,
                "description": f"Test {gravite}",
                "idPatient": patient_en_db.id
            })
            assert response.status_code == 201, f"Échec pour gravité {gravite}"


class TestGetIncident:
    """Tests GET /api/incidents/{id}"""

    def test_get_incident_existant(self, client, incident_en_db):
        """✅ Récupération incident existant → 200"""
        response = client.get(f"/api/incidents/{incident_en_db['id']}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == incident_en_db["id"]
        assert data["description"] == incident_en_db["description"]

    def test_get_incident_inexistant(self, client):
        """❌ ID inexistant → 404"""
        response = client.get("/api/incidents/99999")
        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"].lower()

    def test_get_incident_id_zero(self, client):
        """❌ ID 0 → 404"""
        response = client.get("/api/incidents/0")
        assert response.status_code == 404

    def test_get_incident_structure_reponse(self, client, incident_en_db):
        """✅ Structure de la réponse correcte"""
        response = client.get(f"/api/incidents/{incident_en_db['id']}")
        data = response.json()
        champs_attendus = ["id", "dateIncident", "heureIncident", "gravite", 
                          "description", "statut", "idPatient"]
        for champ in champs_attendus:
            assert champ in data, f"Champ '{champ}' absent de la réponse"


class TestPutIncident:
    """Tests PUT /api/incidents/{id}"""

    def test_update_statut_valide(self, client, incident_en_db):
        """✅ Mise à jour statut → 200"""
        response = client.put(
            f"/api/incidents/{incident_en_db['id']}",
            json={"statut": "Résolu"}
        )
        assert response.status_code == 200
        assert response.json()["statut"] == "Résolu"

    def test_update_incident_inexistant(self, client):
        """❌ ID inexistant → 404"""
        response = client.put("/api/incidents/99999", json={"statut": "Résolu"})
        assert response.status_code == 404

    def test_update_gravite(self, client, incident_en_db):
        """✅ Mise à jour gravité"""
        response = client.put(
            f"/api/incidents/{incident_en_db['id']}",
            json={"gravite": "Critique"}
        )
        assert response.status_code == 200
        assert response.json()["gravite"] == "Critique"


class TestDeleteIncident:
    """Tests DELETE /api/incidents/{id}"""

    def test_delete_incident_existant(self, client, incident_en_db):
        """✅ Soft delete → 204"""
        response = client.delete(f"/api/incidents/{incident_en_db['id']}")
        assert response.status_code == 204

    def test_delete_rend_incident_inaccessible(self, client, incident_en_db):
        """✅ Après delete, GET retourne 404"""
        client.delete(f"/api/incidents/{incident_en_db['id']}")
        response = client.get(f"/api/incidents/{incident_en_db['id']}")
        assert response.status_code == 404

    def test_delete_incident_inexistant(self, client):
        """❌ ID inexistant → 404"""
        response = client.delete("/api/incidents/99999")
        assert response.status_code == 404


class TestPatientIncidents:
    """Tests GET /api/patients/{id}/incidents"""

    def test_liste_incidents_patient(self, client, patient_en_db, incident_valide):
        """✅ Liste des incidents d'un patient"""
        for i in range(3):
            incident_valide["description"] = f"Incident {i+1}"
            client.post("/api/incidents/", json=incident_valide)

        response = client.get(f"/api/patients/{patient_en_db.id}/incidents")
        assert response.status_code == 200
        assert len(response.json()) == 3

    def test_liste_incidents_patient_vide(self, client, patient_en_db):
        """✅ Patient sans incident → liste vide"""
        response = client.get(f"/api/patients/{patient_en_db.id}/incidents")
        assert response.status_code == 200
        assert response.json() == []


class TestSuivisIncident:
    """Tests POST et GET /api/incidents/{id}/suivis"""

    def test_ajout_suivi(self, client, incident_en_db):
        """✅ Ajout d'un suivi → 201"""
        response = client.post(
            f"/api/incidents/{incident_en_db['id']}/suivis",
            json={
                "dateSuivi": "2024-03-25",
                "actionsPrises": "Recalibration effectuée"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["idIncident"] == incident_en_db["id"]

    def test_historique_suivis(self, client, incident_en_db):
        """✅ Récupération historique des suivis"""
        for i in range(2):
            client.post(
                f"/api/incidents/{incident_en_db['id']}/suivis",
                json={"dateSuivi": "2024-03-25", "actionsPrises": f"Action {i+1}"}
            )

        response = client.get(f"/api/incidents/{incident_en_db['id']}/suivis")
        assert response.status_code == 200
        assert len(response.json()) == 2

    def test_suivi_incident_inexistant(self, client):
        """❌ Suivi sur incident inexistant → 404"""
        response = client.post(
            "/api/incidents/99999/suivis",
            json={"dateSuivi": "2024-03-25", "actionsPrises": "Test"}
        )
        assert response.status_code == 404


class TestHealthCheck:
    """Test endpoint santé"""

    def test_health_ok(self, client):
        """✅ Health check retourne 200"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"