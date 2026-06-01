"""
Summary API route: monthly financial overview.
Requires authentication.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.summary import MonthlySummary
from backend.app.services.summary_service import get_monthly_summary

router = APIRouter(prefix="/api/summary", tags=["Summary"])


@router.get("/", response_model=MonthlySummary)
def monthly_summary(
    month: str = Query(
        ...,
        description="Month in YYYY-MM format",
        examples=["2025-05"],
        pattern=r"^\d{4}-\d{2}$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get monthly summary: total income, total expenses, net savings,
    and expenses breakdown by category.
    """
    year, month_num = map(int, month.split("-"))
    return get_monthly_summary(db, current_user.id, year, month_num)
