# BASIC TEST SETUP
import pytest

from backend_api_project.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()

# TEST HOME ROUTE
def test_home(client):
    response = client.get("/")
    assert response.status_code == 200

# TEST REGISTER API
def test_register(client):
    response = client.post("/users", json = {
        "name": "TestUser",
        "age": 22,
        "password": "test123"
    })

    assert response.status_code == 201

# TEST LOGIN API
def test_login(client):
    client.post("/users", json={
        "name": "TestUser2",
        "age": 24,
        "password": "test123"
    })

    from backend_api_project.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET is_verified = TRUE WHERE name = %s",
        ("TestUser2",)
    )
    conn.commit
    conn.close()

    response = client.post("/login", json={
        "name":"TestUser2",
        "password":"test123"
    })

    assert response.status_code == 200
    assert "access_token" in response.json