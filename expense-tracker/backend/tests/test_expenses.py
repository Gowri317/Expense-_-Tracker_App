"""Tests for expense CRUD endpoints."""

from datetime import date


def test_create_expense(client, auth_headers):
    """Create an expense successfully."""
    response = client.post(
        "/api/expenses/",
        json={"amount": 25.50, "category_id": 1, "date": str(date.today()), "note": "Lunch"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 25.50
    assert data["note"] == "Lunch"


def test_list_expenses(client, auth_headers):
    """List expenses returns created entries."""
    client.post(
        "/api/expenses/",
        json={"amount": 10.00, "category_id": 1, "date": str(date.today())},
        headers=auth_headers,
    )
    client.post(
        "/api/expenses/",
        json={"amount": 20.00, "category_id": 2, "date": str(date.today())},
        headers=auth_headers,
    )
    response = client.get("/api/expenses/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_expense(client, auth_headers):
    """Update an expense's amount."""
    create_resp = client.post(
        "/api/expenses/",
        json={"amount": 15.00, "category_id": 1, "date": str(date.today())},
        headers=auth_headers,
    )
    expense_id = create_resp.json()["id"]
    response = client.put(
        f"/api/expenses/{expense_id}",
        json={"amount": 30.00},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["amount"] == 30.00


def test_delete_expense(client, auth_headers):
    """Delete an expense successfully."""
    create_resp = client.post(
        "/api/expenses/",
        json={"amount": 5.00, "category_id": 1, "date": str(date.today())},
        headers=auth_headers,
    )
    expense_id = create_resp.json()["id"]
    response = client.delete(f"/api/expenses/{expense_id}", headers=auth_headers)
    assert response.status_code == 200

    # Verify it's gone
    list_resp = client.get("/api/expenses/", headers=auth_headers)
    assert len(list_resp.json()) == 0


def test_filter_expenses_by_category(client, auth_headers):
    """Filter expenses by category_id."""
    client.post(
        "/api/expenses/",
        json={"amount": 10.00, "category_id": 1, "date": str(date.today())},
        headers=auth_headers,
    )
    client.post(
        "/api/expenses/",
        json={"amount": 20.00, "category_id": 2, "date": str(date.today())},
        headers=auth_headers,
    )
    response = client.get("/api/expenses/?category_id=1", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category_id"] == 1
