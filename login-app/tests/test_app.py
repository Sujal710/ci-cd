import os

os.environ.setdefault("APP_USERNAME", "admin")
os.environ.setdefault("APP_PASSWORD", "password123")

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_login_page_loads():
    response = client.get("/")
    assert response.status_code == 200
    assert "Sign in" in response.text


def test_login_success_redirects_and_sets_cookie():
    response = client.post(
        "/login",
        data={"username": "admin", "password": "password123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/welcome"
    assert "session_id" in response.cookies


def test_login_success_then_welcome_accessible():
    login_response = client.post(
        "/login",
        data={"username": "admin", "password": "password123"},
    )
    assert login_response.status_code == 200
    assert "Welcome" in login_response.text


def test_login_failure_shows_error():
    response = client.post(
        "/login",
        data={"username": "admin", "password": "wrongpass"},
    )
    assert response.status_code == 200
    assert "Invalid username or password" in response.text


def test_login_failure_does_not_set_cookie():
    response = client.post(
        "/login",
        data={"username": "wrong", "password": "wrong"},
    )
    assert "session_id" not in response.cookies


def test_welcome_without_session_redirects_to_login():
    client.cookies.clear()
    response = client.get("/welcome", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"


def test_welcome_with_invalid_session_redirects_to_login():
    client.cookies.set("session_id", "not-a-real-session")
    response = client.get("/welcome", follow_redirects=False)
    assert response.status_code == 303
    client.cookies.clear()


@pytest.mark.parametrize(
    "username,password",
    [
        ("", ""),
        ("admin", ""),
        ("", "password123"),
    ],
)
def test_login_missing_fields_rejected(username, password):
    response = client.post(
        "/login",
        data={"username": username, "password": password},
    )
    assert response.status_code == 200
    assert "Invalid username or password" in response.text
