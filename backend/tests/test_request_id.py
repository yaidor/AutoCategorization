from fastapi.testclient import TestClient

from app.main import app


def test_request_id_is_generated_when_missing() -> None:
    client = TestClient(app)
    response = client.get("/health")
    request_id = response.headers.get("X-Request-ID")
    assert request_id
    assert len(request_id) >= 16


def test_request_id_is_preserved_from_client() -> None:
    client = TestClient(app)
    custom_id = "client-supplied-12345"
    response = client.get("/health", headers={"X-Request-ID": custom_id})
    assert response.headers["X-Request-ID"] == custom_id


def test_request_ids_are_unique_across_requests() -> None:
    client = TestClient(app)
    first = client.get("/health").headers["X-Request-ID"]
    second = client.get("/health").headers["X-Request-ID"]
    assert first != second
