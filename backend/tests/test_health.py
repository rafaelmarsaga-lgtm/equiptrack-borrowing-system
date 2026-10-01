from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_ok():
    # "with" runs the lifespan, which creates the tables
    with TestClient(app) as client:
        response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
