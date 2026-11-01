from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_health_without_auth_header_fails():
    response = client.get("/internal/v1/health")
    assert response.status_code in (403, 422) # Missing header or forbidden

def test_health_with_valid_key_succeeds():
    headers = {"X-Internal-Service-Key": settings.internal_service_key}
    response = client.get("/internal/v1/health", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "knowdoc-ai-service"
    assert data["status"] == "healthy"

