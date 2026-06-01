"""
Test fixtures: test database, test client, and authenticated user helper.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.db.base import Base
from backend.app.db.database import get_db
from backend.app.main import app
from backend.app.db.init_db import DEFAULT_CATEGORIES
from backend.app.models.category import Category


# In-memory SQLite for tests
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    # Seed default categories
    db = TestSessionLocal()
    for name in DEFAULT_CATEGORIES:
        db.add(Category(name=name, user_id=None))
    db.commit()
    db.close()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers with JWT token."""
    client.post("/api/auth/register", json={"username": "testuser", "password": "testpass123"})
    response = client.post("/api/auth/login", json={"username": "testuser", "password": "testpass123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
