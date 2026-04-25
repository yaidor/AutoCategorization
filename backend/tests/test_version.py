from fastapi.testclient import TestClient

from app.main import app


def test_version_exposes_metadata() -> None:
    client = TestClient(app)
    response = client.get("/version")
    assert response.status_code == 200
    body = response.json()
    assert "version" in body
    assert body["version"]
    assert body["environment"] == "development"
