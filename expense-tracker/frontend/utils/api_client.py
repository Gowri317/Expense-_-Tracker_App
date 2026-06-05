"""
API Client: httpx-based wrapper for all backend API calls.
Injects auth token from Streamlit session state automatically.
Includes retry logic for Render free-tier cold starts.
"""

import os
import time
import httpx
import streamlit as st
from datetime import date
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Render free tier config
MAX_RETRIES = 5         # Retry up to 5 times for cold starts
RETRY_DELAY = 10        # Wait 10 seconds between retries
REQUEST_TIMEOUT = 60    # 60 second timeout per request


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
            detail = response.text or "Unknown error"
        return {"error": True, "detail": detail, "status_code": response.status_code}
    return response.json()


def _is_cold_start_error(response: httpx.Response) -> bool:
    """Check if the error is from Render's proxy (backend sleeping)."""
    if response.status_code == 404:
        try:
            body = response.text.strip()
            # Render proxy returns plain "Not Found" (not JSON)
            if body == "Not Found" or body == '{"detail":"Not Found"}':
                return True
        except Exception:
            pass
    # Also handle 502/503 which Render may return during spin-up
    if response.status_code in (502, 503):
        return True
    return False


def _request_with_retry(method: str, url: str, **kwargs) -> httpx.Response:
    """
    Make an HTTP request with automatic retry for Render cold starts.
    When the backend is sleeping, Render returns 404. We retry until it wakes up.
    """
    last_response = None
    
    for attempt in range(MAX_RETRIES):
        try:
            with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
                response = getattr(client, method)(url, **kwargs)
                
                # If it's a cold start error, retry
                if _is_cold_start_error(response) and attempt < MAX_RETRIES - 1:
                    last_response = response
                    time.sleep(RETRY_DELAY)
                    continue
                
                return response
                
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.ConnectTimeout) as e:
            last_response = None
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            # Create a fake response for the error
            raise
    
    # If all retries failed, return the last response
    if last_response is not None:
        return last_response
    raise httpx.ConnectError("Backend is unreachable after multiple retries")


# ─── Auth ────────────────────────────────────────────────────────────────────

def register(username: str, password: str) -> dict:
    """Register a new user."""
    try:
        resp = _request_with_retry(
            "post",
            f"{BACKEND_URL}/api/auth/register",
            json={"username": username, "password": password},
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def login(username: str, password: str) -> dict:
    """Login and return token data."""
    try:
        resp = _request_with_retry(
            "post",
            f"{BACKEND_URL}/api/auth/login",
            json={"username": username, "password": password},
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


# ─── Categories ──────────────────────────────────────────────────────────────

def get_categories() -> list:
    """Get all categories available to the user."""
    try:
        resp = _request_with_retry("get", f"{BACKEND_URL}/api/categories/", headers=_get_headers())
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def create_category(name: str) -> dict:
    """Create a custom category."""
    try:
        resp = _request_with_retry(
            "post",
            f"{BACKEND_URL}/api/categories/",
            json={"name": name},
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


# ─── Expenses ────────────────────────────────────────────────────────────────

def create_expense(amount: float, category_id: int, expense_date: date, note: str = "") -> dict:
    """Create a new expense."""
    try:
        resp = _request_with_retry(
            "post",
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
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


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

    try:
        resp = _request_with_retry(
            "get",
            f"{BACKEND_URL}/api/expenses/",
            params=params,
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def update_expense(expense_id: int, **kwargs) -> dict:
    """Update an expense by ID."""
    if "date" in kwargs and kwargs["date"]:
        kwargs["date"] = str(kwargs["date"])
    try:
        resp = _request_with_retry(
            "put",
            f"{BACKEND_URL}/api/expenses/{expense_id}",
            json=kwargs,
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def delete_expense(expense_id: int) -> dict:
    """Delete an expense by ID."""
    try:
        resp = _request_with_retry(
            "delete",
            f"{BACKEND_URL}/api/expenses/{expense_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


# ─── Income ──────────────────────────────────────────────────────────────────

def create_income(amount: float, source: str, income_date: date) -> dict:
    """Create a new income entry."""
    try:
        resp = _request_with_retry(
            "post",
            f"{BACKEND_URL}/api/income/",
            json={
                "amount": amount,
                "source": source,
                "date": str(income_date),
            },
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


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

    try:
        resp = _request_with_retry(
            "get",
            f"{BACKEND_URL}/api/income/",
            params=params,
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def update_income(income_id: int, **kwargs) -> dict:
    """Update an income entry by ID."""
    if "date" in kwargs and kwargs["date"]:
        kwargs["date"] = str(kwargs["date"])
    try:
        resp = _request_with_retry(
            "put",
            f"{BACKEND_URL}/api/income/{income_id}",
            json=kwargs,
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def delete_income(income_id: int) -> dict:
    """Delete an income entry by ID."""
    try:
        resp = _request_with_retry(
            "delete",
            f"{BACKEND_URL}/api/income/{income_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


# ─── Summary ─────────────────────────────────────────────────────────────────

def get_summary(month: str) -> dict:
    """Get monthly summary (YYYY-MM format)."""
    try:
        resp = _request_with_retry(
            "get",
            f"{BACKEND_URL}/api/summary/",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


# ─── Budgets ─────────────────────────────────────────────────────────────────

def get_budgets(month: str) -> list:
    """Get all budgets for the given month (YYYY-MM)."""
    try:
        resp = _request_with_retry(
            "get",
            f"{BACKEND_URL}/api/budgets/",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def set_budget(category_id: int, amount: float, month: str) -> dict:
    """Set or update a budget limit for a category."""
    try:
        resp = _request_with_retry(
            "post",
            f"{BACKEND_URL}/api/budgets/",
            json={"category_id": category_id, "amount": amount, "month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def delete_budget(budget_id: int) -> dict:
    """Delete a budget limit."""
    try:
        resp = _request_with_retry(
            "delete",
            f"{BACKEND_URL}/api/budgets/{budget_id}",
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}


def get_budget_progress(month: str) -> list:
    """Get budget progress details (spending vs limit) for the given month."""
    try:
        resp = _request_with_retry(
            "get",
            f"{BACKEND_URL}/api/budgets/progress",
            params={"month": month},
            headers=_get_headers(),
        )
        return _handle_response(resp)
    except Exception as e:
        return {"error": True, "detail": f"Could not reach server: {e}", "status_code": 0}
