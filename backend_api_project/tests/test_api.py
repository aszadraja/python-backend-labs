# BASIC TEST SETUP
import pytest
import time

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
    username = "TestUser_" + str(time.time())

    response = client.post("/users", json = {
        "name": username,
        "age": 22,
        "password": "test123"
    })

    assert response.status_code == 201

# TEST LOGIN API
def test_login(client):
    username = "TestUser_" + str(time.time()).lower()

    res = client.post("/users", json={
        "name": username,
        "age": 24,
        "password": "test123"
    })
    assert res.status_code == 201

    from backend_api_project.database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE users SET is_verified = TRUE, verification_token = NULL WHERE Lower(name) = LOWER(%s) ",
        (username,)
    )

    conn.commit()
    conn.close()

    response = client.post("/login", json={
        "name":username,
        "password":"test123"
    })
    print(response.status_code)
    print(response.json)

    assert response.status_code == 200
    assert "access_token" in response.json