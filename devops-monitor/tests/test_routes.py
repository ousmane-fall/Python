import os

from fastapi.testclient import TestClient

from api.main import app, reset_store


client = TestClient(app)


def setup_function():
    os.environ["DISABLE_POLL_LOOP"] = "1"
    reset_store()


def test_health_route():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics_route():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "cpu_percent" in response.json()


def test_post_server_without_key_returns_403():
    response = client.post(
        "/servers",
        json={"name": "api-1", "host": "10.0.0.1", "port": 8080},
    )
    assert response.status_code == 403


def test_post_server_with_valid_key_then_list():
    response = client.post(
        "/servers",
        json={"name": "api-1", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": "dev-secret-key"},
    )
    assert response.status_code == 201
    server_id = response.json()["id"]

    response = client.get("/servers")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == server_id


def test_get_nonexistent_server_returns_404():
    response = client.get("/servers/999")
    assert response.status_code == 404
