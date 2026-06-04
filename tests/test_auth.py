import uuid

from fastapi.testclient import TestClient

from app.main import app
client = TestClient(app)

def test_register_user():
    username=f"testuser_{uuid.uuid4().hex}"
    response = client.post("/auth/register", json={
        "username": username,
        "password": "test1234",

    })
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert "id" in data
    assert "password" not in data

def test_login_success():
    username=f"testuser_{uuid.uuid4().hex}"
    password = "test1234"
    client.post("/auth/register", json={
        "username": username,
        "password": password
    })
    response = client.post("/auth/login", json={
        "username": username,
        "password": password
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password():
    username=f"testuser_{uuid.uuid4().hex}"
    client.post("/auth/register", json={
        "username": username,
        "password": "rtest1234"
    })
    response = client.post("/auth/login", json={
        "username": username,
        "password": "wtest1234"
    })
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data
    assert "access_token" not in data


def test_events_list_requires_login():
    response = client.get("/events/")
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


