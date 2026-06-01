"""
Income service: CRUD operations.
"""

from typing import Optional, List
from datetime import date

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.app.models.income import Income
from backend.app.schemas.income import IncomeCreate, IncomeUpdate


def create_income(db: Session, income_data: IncomeCreate, user_id: int) -> Income:
    """Create a new income entry for the given user."""
    income = Income(
        amount=income_data.amount,
        source=income_data.source,
        date=income_data.date,
        user_id=user_id,
    )
    db.add(income)
    db.commit()
    db.refresh(income)
    return income


def get_incomes(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Income]:
    """List income entries for a user with optional date range filter."""
    query = db.query(Income).filter(Income.user_id == user_id)

    if start_date:
        query = query.filter(Income.date >= start_date)
    if end_date:
        query = query.filter(Income.date <= end_date)

    return query.order_by(Income.date.desc()).offset(skip).limit(limit).all()


def get_income_by_id(db: Session, income_id: int, user_id: int) -> Income:
    """Get a single income entry by ID. Raises 404 if not found or not owned by user."""
    income = (
        db.query(Income)
        .filter(Income.id == income_id, Income.user_id == user_id)
        .first()
    )
    if not income:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Income entry not found",
        )
    return income


def update_income(
    db: Session, income_id: int, user_id: int, income_data: IncomeUpdate
) -> Income:
    """Update an existing income entry. Only updates provided fields."""
    income = get_income_by_id(db, income_id, user_id)
    update_data = income_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(income, field, value)

    db.commit()
    db.refresh(income)
    return income


def delete_income(db: Session, income_id: int, user_id: int) -> dict:
    """Delete an income entry by ID. Returns success message."""
    income = get_income_by_id(db, income_id, user_id)
    db.delete(income)
    db.commit()
    return {"message": "Income deleted successfully"}
