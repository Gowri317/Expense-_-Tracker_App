"""Tests for authentication endpoints."""


def test_health_check(client):
    """Health endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user(client):
    """Register a new user successfully."""
    response = client.post(
        "/api/auth/register",
        json={"username": "newuser", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data


def test_register_duplicate_username(client):
    """Cannot register with an existing username."""
    client.post("/api/auth/register", json={"username": "dupe", "password": "password123"})
    response = client.post("/api/auth/register", json={"username": "dupe", "password": "password123"})
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    """Login returns a JWT token."""
    client.post("/api/auth/register", json={"username": "loginuser", "password": "password123"})
    response = client.post("/api/auth/login", json={"username": "loginuser", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    """Login with wrong password returns 401."""
    client.post("/api/auth/register", json={"username": "user2", "password": "password123"})
    response = client.post("/api/auth/login", json={"username": "user2", "password": "wrongpass"})
    assert response.status_code == 401


def test_protected_route_without_token(client):
    """Accessing protected route without token returns 401."""
    response = client.get("/api/expenses/")
    assert response.status_code == 401
