"""
API Client: httpx-based wrapper for all backend API calls.
Injects auth token from Streamlit session state automatically.
"""

import os
import httpx
import streamlit as st
from datetime import date
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def _get_headers() -> dict:
    """Get authorization headers from session state."""
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def _handle_response(response: httpx.Response) -> Any:
    """Handle API response and raise errors with clear messages."""
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", "Unknown error")
        except Exception:
            detail = response.text
        return {"error": True, "detail": detail, "status_code": response.status_code}
    return response.json()


# ─── Auth ────────────────────────────────────────────────────────────────────

def register(username: str, password: str) -> dict:
    """Register a new user."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "password": password},
        )
        return _handle_response(resp)


def login(username: str, password: str) -> dict:
    """Login and return token data."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password},
        )
        return _handle_response(resp)


# ─── Categories ──────────────────────────────────────────────────────────────

def get_categories() -> list:
    """Get all categories available to the user."""
    with httpx.Client(timeout=10) as client:
        resp = client.get(f"{BACKEND_URL}/api/categories/", headers=_get_headers())
        return _handle_response(resp)


def create_category(name: str) -> dict:
    """Create a custom category."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/categories/",
            json={"name": name},
            headers=_get_headers(),
        )
        return _handle_response(resp)


# ─── Expenses ────────────────────────────────────────────────────────────────

def create_expense(amount: float, category_id: int, expense_date: date, note: str = "") -> dict:
    """Create a new expense."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/expenses/",
            json={
                "amount": amount,
                "category_id": category_id,
                "date": str(expense_date),
                "note": note or None,
            },
            headers=_get_headers(),
        )
        return _handle_response(resp)


def get_expenses(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
) -> list:
    """Get expenses with optional filters."""
    params = {}
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)
    if category_id:
        params["category_id"] = category_id

    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{BACKEND_URL}/api/expenses/",
            params=params,
            headers=_get_headers(),
        )
        return _handle_response(resp)


def update_expense(expense_id: int, **kwargs) -> dict:
    """Update an expense by ID."""
    # Convert date to string if present
    if "date" in kwargs and kwargs["date"]:
        kwargs["date"] = str(kwargs["date"])
    with httpx.Client(timeout=10) as client:
        resp = client.put(
            f"{BACKEND_URL}/api/expenses/{expense_id}",
            json=kwargs,
            headers=_get_headers(),
        )
        return _handle_response(resp)


def delete_expense(expense_id: int) -> dict:
    """Delete an expense by ID."""
    with httpx.Client(timeout=10) as client:
        resp = client.delete(
            f"{BACKEND_URL}/api/expenses/{expense_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)


# ─── Income ──────────────────────────────────────────────────────────────────

def create_income(amount: float, source: str, income_date: date) -> dict:
    """Create a new income entry."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/income/",
            json={
                "amount": amount,
                "source": source,
                "date": str(income_date),
            },
            headers=_get_headers(),
        )
        return _handle_response(resp)


def get_incomes(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> list:
    """Get income entries with optional date filter."""
    params = {}
    if start_date:
        params["start_date"] = str(start_date)
    if end_date:
        params["end_date"] = str(end_date)

    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{BACKEND_URL}/api/income/",
            params=params,
            headers=_get_headers(),
        )
        return _handle_response(resp)


def update_income(income_id: int, **kwargs) -> dict:
    """Update an income entry by ID."""
    if "date" in kwargs and kwargs["date"]:
        kwargs["date"] = str(kwargs["date"])
    with httpx.Client(timeout=10) as client:
        resp = client.put(
            f"{BACKEND_URL}/api/income/{income_id}",
            json=kwargs,
            headers=_get_headers(),
        )
        return _handle_response(resp)


def delete_income(income_id: int) -> dict:
    """Delete an income entry by ID."""
    with httpx.Client(timeout=10) as client:
        resp = client.delete(
            f"{BACKEND_URL}/api/income/{income_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)


# ─── Summary ─────────────────────────────────────────────────────────────────

def get_summary(month: str) -> dict:
    """Get monthly summary (YYYY-MM format)."""
    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{BACKEND_URL}/api/summary/",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)


# ─── Budgets ─────────────────────────────────────────────────────────────────

def get_budgets(month: str) -> list:
    """Get all budgets for the given month (YYYY-MM)."""
    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{BACKEND_URL}/api/budgets/",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)


def set_budget(category_id: int, amount: float, month: str) -> dict:
    """Set or update a budget limit for a category."""
    with httpx.Client(timeout=10) as client:
        resp = client.post(
            f"{BACKEND_URL}/api/budgets/",
            json={"category_id": category_id, "amount": amount, "month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)


def delete_budget(budget_id: int) -> dict:
    """Delete a budget limit."""
    with httpx.Client(timeout=10) as client:
        resp = client.delete(
            f"{BACKEND_URL}/api/budgets/{budget_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)


def get_budget_progress(month: str) -> list:
    """Get budget progress details (spending vs limit) for the given month."""
    with httpx.Client(timeout=10) as client:
        resp = client.get(
            f"{BACKEND_URL}/api/budgets/progress",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)
