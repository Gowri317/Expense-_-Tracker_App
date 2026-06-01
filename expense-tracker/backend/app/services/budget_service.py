"""Budget service: CRUD operations and progress calculations."""

import calendar
from datetime import date
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status

from backend.app.models.budget import Budget
from backend.app.models.category import Category
from backend.app.models.expense import Expense
from backend.app.schemas.budget import BudgetCreate, CategoryBudgetProgress


def set_budget(db: Session, user_id: int, budget_data: BudgetCreate) -> Budget:
    """Create or update (upsert) a budget limit for a category in a month."""
    # Verify category exists
    category = db.query(Category).filter(Category.id == budget_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    # Check if budget already exists for this user + category + month
    existing = db.query(Budget).filter(
        Budget.user_id == user_id,
        Budget.category_id == budget_data.category_id,
        Budget.month == budget_data.month
    ).first()

    if existing:
        existing.amount = budget_data.amount
        db.commit()
        db.refresh(existing)
        return existing

    # Create new budget
    budget = Budget(
        user_id=user_id,
        category_id=budget_data.category_id,
        amount=budget_data.amount,
        month=budget_data.month
    )
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def get_budgets(db: Session, user_id: int, month: str) -> List[Budget]:
    """Get all budget limits set by a user for a specific month."""
    return (
        db.query(Budget)
        .options(joinedload(Budget.category))
        .filter(Budget.user_id == user_id, Budget.month == month)
        .all()
    )


def delete_budget(db: Session, budget_id: int, user_id: int) -> dict:
    """Delete a budget limit."""
    budget = db.query(Budget).filter(Budget.id == budget_id, Budget.user_id == user_id).first()
    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget limit not found",
        )
    db.delete(budget)
    db.commit()
    return {"message": "Budget limit deleted successfully"}


def get_budget_progress(db: Session, user_id: int, year: int, month_num: int) -> List[CategoryBudgetProgress]:
    """
    Calculate spending progress against budget limits for a given month.
    Only returns progress for categories that have a budget set.
    """
    month_str = f"{year}-{month_num:02d}"

    # 1. Fetch all budgets set for the month
    budgets = (
        db.query(Budget)
        .options(joinedload(Budget.category))
        .filter(Budget.user_id == user_id, Budget.month == month_str)
        .all()
    )

    if not budgets:
        return []

    # 2. Fetch all expenses for this month
    start_date = date(year, month_num, 1)
    _, last_day = calendar.monthrange(year, month_num)
    end_date = date(year, month_num, last_day)

    expenses = (
        db.query(Expense)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date
        )
        .all()
    )

    # 3. Aggregate expenses by category
    spending_by_category: Dict[int, float] = {}
    for exp in expenses:
        spending_by_category[exp.category_id] = spending_by_category.get(exp.category_id, 0.0) + exp.amount

    # 4. Construct progress list
    progress_list = []
    for b in budgets:
        spent = spending_by_category.get(b.category_id, 0.0)
        percentage = (spent / b.amount) * 100 if b.amount > 0 else 0.0
        progress_list.append(
            CategoryBudgetProgress(
                category_id=b.category_id,
                category_name=b.category.name if b.category else "Unknown",
                amount_spent=spent,
                budget_limit=b.amount,
                percentage_used=percentage
            )
        )

    return progress_list
