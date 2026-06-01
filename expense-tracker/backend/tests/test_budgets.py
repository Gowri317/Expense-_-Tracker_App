"""Tests for budget CRUD and progress endpoints."""

from datetime import date


def test_create_and_update_budget(client, auth_headers):
    """Create a budget limit, then update it via the upsert mechanism."""
    # First, list categories to get a valid category ID
    cat_resp = client.get("/api/categories/", headers=auth_headers)
    assert cat_resp.status_code == 200
    category_id = cat_resp.json()[0]["id"]

    # Create budget
    response = client.post(
        "/api/budgets/",
        json={"category_id": category_id, "amount": 500.0, "month": "2026-06"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["amount"] == 500.0
    assert data["month"] == "2026-06"
    assert data["category_id"] == category_id

    # Update (upsert) budget
    update_response = client.post(
        "/api/budgets/",
        json={"category_id": category_id, "amount": 750.0, "month": "2026-06"},
        headers=auth_headers,
    )
    assert update_response.status_code == 201
    update_data = update_response.json()
    assert update_data["id"] == data["id"]  # Check it's the same record
    assert update_data["amount"] == 750.0


def test_list_budgets(client, auth_headers):
    """List budget limits for a specific month."""
    cat_resp = client.get("/api/categories/", headers=auth_headers)
    category_id = cat_resp.json()[0]["id"]

    client.post(
        "/api/budgets/",
        json={"category_id": category_id, "amount": 1000.0, "month": "2026-06"},
        headers=auth_headers,
    )

    # Get budgets for matching month
    list_resp = client.get("/api/budgets/?month=2026-06", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1
    assert list_resp.json()[0]["amount"] == 1000.0

    # Get budgets for different month (should be empty)
    list_resp_empty = client.get("/api/budgets/?month=2026-07", headers=auth_headers)
    assert list_resp_empty.status_code == 200
    assert len(list_resp_empty.json()) == 0


def test_delete_budget(client, auth_headers):
    """Delete a budget limit."""
    cat_resp = client.get("/api/categories/", headers=auth_headers)
    category_id = cat_resp.json()[0]["id"]

    create_resp = client.post(
        "/api/budgets/",
        json={"category_id": category_id, "amount": 400.0, "month": "2026-06"},
        headers=auth_headers,
    )
    budget_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/budgets/{budget_id}", headers=auth_headers)
    assert delete_resp.status_code == 200

    # Verify list is empty
    list_resp = client.get("/api/budgets/?month=2026-06", headers=auth_headers)
    assert len(list_resp.json()) == 0


def test_budget_progress(client, auth_headers):
    """Calculate progress comparing expenses against set budgets."""
    cat_resp = client.get("/api/categories/", headers=auth_headers)
    category_id = cat_resp.json()[0]["id"]

    # Set budget of 1000 for 2026-06
    client.post(
        "/api/budgets/",
        json={"category_id": category_id, "amount": 1000.0, "month": "2026-06"},
        headers=auth_headers,
    )

    # Add expense of 350 on 2026-06-15
    client.post(
        "/api/expenses/",
        json={
            "amount": 350.0,
            "category_id": category_id,
            "date": "2026-06-15",
            "note": "Groceries",
        },
        headers=auth_headers,
    )

    # Get budget progress for 2026-06
    progress_resp = client.get("/api/budgets/progress?month=2026-06", headers=auth_headers)
    assert progress_resp.status_code == 200
    progress_data = progress_resp.json()
    assert len(progress_data) == 1
    assert progress_data[0]["category_id"] == category_id
    assert progress_data[0]["amount_spent"] == 350.0
    assert progress_data[0]["budget_limit"] == 1000.0
    assert progress_data[0]["percentage_used"] == 35.0
