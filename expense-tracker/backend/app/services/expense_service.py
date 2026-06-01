"""
Expense service: CRUD operations with filtering support.
"""

from datetime import date
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from backend.app.models.expense import Expense
from backend.app.models.category import Category
from backend.app.schemas.expense import ExpenseCreate, ExpenseUpdate


def create_expense(db: Session, expense_data: ExpenseCreate, user_id: int) -> Expense:
    """Create a new expense for the given user."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == expense_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    expense = Expense(
        amount=expense_data.amount,
        category_id=expense_data.category_id,
        date=expense_data.date,
        note=expense_data.note,
        user_id=user_id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


def get_expenses(
    db: Session,
    user_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Expense]:
    """List expenses for a user with optional date range and category filters."""
    query = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.user_id == user_id)
    )

    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    if category_id:
        query = query.filter(Expense.category_id == category_id)

    return query.order_by(Expense.date.desc()).offset(skip).limit(limit).all()


def get_expense_by_id(db: Session, expense_id: int, user_id: int) -> Expense:
    """Get a single expense by ID. Raises 404 if not found or not owned by user."""
    expense = (
        db.query(Expense)
        .options(joinedload(Expense.category))
        .filter(Expense.id == expense_id, Expense.user_id == user_id)
        .first()
    )
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    return expense


def update_expense(
    db: Session, expense_id: int, user_id: int, expense_data: ExpenseUpdate
) -> Expense:
    """Update an existing expense. Only updates provided fields."""
    expense = get_expense_by_id(db, expense_id, user_id)
    update_data = expense_data.model_dump(exclude_unset=True)

    if "category_id" in update_data:
        category = db.query(Category).filter(Category.id == update_data["category_id"]).first()
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )

    for field, value in update_data.items():
        setattr(expense, field, value)

    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int, user_id: int) -> dict:
    """Delete an expense by ID. Returns success message."""
    expense = get_expense_by_id(db, expense_id, user_id)
    db.delete(expense)
    db.commit()
    return {"message": "Expense deleted successfully"}
