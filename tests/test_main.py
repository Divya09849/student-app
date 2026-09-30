from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
    response = client.get("/")

    assert response.status_code == 200

    data = response.json()

    assert data["application"] == "student-app"
    assert data["message"] == "Student GitOps Application is running"
    assert data["version"] == "1.0.0"
    assert data["environment"] == "dev"
    assert "hostname" in data


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "healthy"
    assert data["application"] == "student-app"


def test_ready():
    response = client.get("/ready")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ready"
    assert data["application"] == "student-app"


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200

    assert "student_app_http_requests_total" in response.text

    assert (
        "student_app_http_request_duration_seconds"
        in response.text
    )