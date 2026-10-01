import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_register_and_login_flow(client: TestClient):
    email = "newuser.auth@example.com"
    payload = {
        "name": "New Auth User",
        "email": email,
        "password": "StrongPass123!",
    }

    register_response = client.post("/api/auth/register", json=payload)
    assert register_response.status_code == 201
    register_data = register_response.json()
    assert register_data["user"]["email"] == email
    assert register_data["user"]["name"] == "New Auth User"

    login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "StrongPass123!"},
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert login_data["user"]["email"] == email
    assert login_data["user"]["id"] == register_data["user"]["id"]

    bad_login_response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "wrong-password"},
    )
    assert bad_login_response.status_code == 401


def test_register_requires_unique_email(client: TestClient):
    payload = {
        "name": "Duplicate User",
        "email": "duplicate.auth@example.com",
        "password": "StrongPass123!",
    }

    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409
