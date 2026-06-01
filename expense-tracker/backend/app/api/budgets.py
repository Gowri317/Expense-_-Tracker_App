"""Budget API routes."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.budget import BudgetCreate, BudgetResponse, CategoryBudgetProgress
from backend.app.services.budget_service import (
    set_budget,
    get_budgets,
    delete_budget,
    get_budget_progress,
)

router = APIRouter(prefix="/api/budgets", tags=["Budgets"])


@router.post("/", response_model=BudgetResponse, status_code=201)
def add_or_update_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set or update a monthly budget limit for a category."""
    budget = set_budget(db, current_user.id, budget_data)
    return BudgetResponse(
        id=budget.id,
        category_id=budget.category_id,
        category_name=budget.category.name if budget.category else "Unknown",
        amount=budget.amount,
        month=budget.month,
        user_id=budget.user_id,
        created_at=budget.created_at,
    )


@router.get("/", response_model=List[BudgetResponse])
def list_budgets(
    month: str = Query(
        ...,
        description="Month in YYYY-MM format",
        pattern=r"^\d{4}-\d{2}$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all budget limits configured for the given month."""
    budgets = get_budgets(db, current_user.id, month)
    return [
        BudgetResponse(
            id=b.id,
            category_id=b.category_id,
            category_name=b.category.name if b.category else "Unknown",
            amount=b.amount,
            month=b.month,
            user_id=b.user_id,
            created_at=b.created_at,
        )
        for b in budgets
    ]


@router.delete("/{budget_id}")
def remove_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a budget limit."""
    return delete_budget(db, budget_id, current_user.id)


@router.get("/progress", response_model=List[CategoryBudgetProgress])
def budget_progress(
    month: str = Query(
        ...,
        description="Month in YYYY-MM format",
        pattern=r"^\d{4}-\d{2}$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get category spending progress vs budgets set for the month."""
    year, month_num = map(int, month.split("-"))
    return get_budget_progress(db, current_user.id, year, month_num)
