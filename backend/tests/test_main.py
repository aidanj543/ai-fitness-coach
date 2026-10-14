from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_welcome():
    response = client.get("/welcome")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the AI Fitness Coach API."

