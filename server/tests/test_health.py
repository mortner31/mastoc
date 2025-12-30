"""
Tests pour les endpoints health.
"""


def test_root(client):
    """Test endpoint racine."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "mastoc-api"
    assert data["version"] == "0.1.0"
    assert data["docs"] == "/docs"


def test_health_check(client):
    """Test endpoint health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app_name"] == "mastoc-api"
    assert data["database"] == "ok"
