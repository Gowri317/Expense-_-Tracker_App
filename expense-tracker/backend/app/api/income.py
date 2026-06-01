"""
Income API routes: full CRUD.
All routes require authentication.
"""

from datetime import date
from typing import Optional, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from backend.app.services.income_service import (
    create_income,
    get_incomes,
    update_income,
    delete_income,
)

router = APIRouter(prefix="/api/income", tags=["Income"])


@router.post("/", response_model=IncomeResponse, status_code=201)
def add_income(
    income_data: IncomeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a new income entry (amount, source, date)."""
    return create_income(db, income_data, current_user.id)


@router.get("/", response_model=List[IncomeResponse])
def list_income(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List income entries with optional date range filter."""
    return get_incomes(db, current_user.id, start_date, end_date, skip, limit)


@router.put("/{income_id}", response_model=IncomeResponse)
def edit_income(
    income_id: int,
    income_data: IncomeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Edit an existing income entry."""
    return update_income(db, income_id, current_user.id, income_data)


@router.delete("/{income_id}")
def remove_income(
    income_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an income entry by ID."""
    return delete_income(db, income_id, current_user.id)
