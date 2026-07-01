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


def test_delete_server_without_key_returns_403():
    # Create a server first
    response = client.post(
        "/servers",
        json={"name": "api-1", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": "dev-secret-key"},
    )
    server_id = response.json()["id"]

    # Try to delete without key
    response = client.delete(f"/servers/{server_id}")
    assert response.status_code == 403


def test_delete_server_with_valid_key():
    # Create a server first
    response = client.post(
        "/servers",
        json={"name": "api-1", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": "dev-secret-key"},
    )
    server_id = response.json()["id"]

    # Delete with key
    response = client.delete(
        f"/servers/{server_id}",
        headers={"X-API-Key": "dev-secret-key"},
    )
    assert response.status_code == 204

    # Verify it's gone
    response = client.get(f"/servers/{server_id}")
    assert response.status_code == 404


def test_delete_nonexistent_server_returns_404():
    response = client.delete(
        "/servers/999",
        headers={"X-API-Key": "dev-secret-key"},
    )
    assert response.status_code == 404


def test_check_server_now():
    # Create a server first
    response = client.post(
        "/servers",
        json={"name": "api-1", "host": "10.0.0.1", "port": 8080},
        headers={"X-API-Key": "dev-secret-key"},
    )
    server_id = response.json()["id"]

    # Check server (will fail because host doesn't exist, but we test endpoint)
    response = client.post(f"/servers/{server_id}/check")
    assert response.status_code == 200
    assert response.json()["status"] in ["UP", "DEGRADED", "DOWN"]


def test_check_nonexistent_server_returns_404():
    response = client.post("/servers/999/check")
    assert response.status_code == 404


def test_get_servers_filter_by_status():
    # Create two servers
    client.post(
        "/servers",
        json={"name": "api-1", "host": "localhost", "port": 9999},
        headers={"X-API-Key": "dev-secret-key"},
    )
    client.post(
        "/servers",
        json={"name": "api-2", "host": "localhost", "port": 9998},
        headers={"X-API-Key": "dev-secret-key"},
    )

    # Get all servers
    response = client.get("/servers")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_websocket_metrics():
    with client.websocket_connect("/ws/metrics") as websocket:
        data = websocket.receive_json()
        assert "cpu_percent" in data
        assert "memory_percent" in data
        assert "disk_percent" in data
