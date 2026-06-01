"""Tests for income CRUD endpoints."""

from datetime import date


def test_create_income(client, auth_headers):
    """Create an income entry successfully."""
    response = client.post(
        "/api/income/",
        json={"amount": 3000.00, "source": "Freelance", "date": str(date.today())},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 3000.00
    assert data["source"] == "Freelance"


def test_list_income(client, auth_headers):
    """List income returns created entries."""
    client.post(
        "/api/income/",
        json={"amount": 1000.00, "source": "Salary", "date": str(date.today())},
        headers=auth_headers,
    )
    response = client.get("/api/income/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_update_income(client, auth_headers):
    """Update an income entry's amount."""
    create_resp = client.post(
        "/api/income/",
        json={"amount": 500.00, "source": "Side gig", "date": str(date.today())},
        headers=auth_headers,
    )
    income_id = create_resp.json()["id"]
    response = client.put(
        f"/api/income/{income_id}",
        json={"amount": 750.00},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 750.00


def test_delete_income(client, auth_headers):
    """Delete an income entry successfully."""
    create_resp = client.post(
        "/api/income/",
        json={"amount": 100.00, "source": "Gift", "date": str(date.today())},
        headers=auth_headers,
    )
    income_id = create_resp.json()["id"]
    response = client.delete(f"/api/income/{income_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify it's gone
    list_resp = client.get("/api/income/", headers=auth_headers)
    assert len(list_resp.json()) == 0
