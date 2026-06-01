"""
Summary service: monthly totals and category breakdown.
"""

from datetime import date
from calendar import monthrange

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.models.expense import Expense
from backend.app.models.income import Income
from backend.app.models.category import Category
from backend.app.schemas.summary import MonthlySummary, CategoryBreakdown


def get_monthly_summary(db: Session, user_id: int, year: int, month: int) -> MonthlySummary:
    """Calculate monthly totals: income, expenses, net savings, and category breakdown."""
    start_date = date(year, month, 1)
    _, last_day = monthrange(year, month)
    end_date = date(year, month, last_day)

    # Total expenses for the month
    total_expenses_result = (
        db.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .scalar()
    )
    total_expenses = float(total_expenses_result)

    # Total income for the month
    total_income_result = (
        db.query(func.coalesce(func.sum(Income.amount), 0.0))
        .filter(
            Income.user_id == user_id,
            Income.date >= start_date,
            Income.date <= end_date,
        )
        .scalar()
    )
    total_income = float(total_income_result)

    # Category breakdown
    category_totals = (
        db.query(
            Category.name,
            func.sum(Expense.amount).label("total"),
        )
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == user_id,
            Expense.date >= start_date,
            Expense.date <= end_date,
        )
        .group_by(Category.name)
        .all()
    )

    breakdown = []
    for cat_name, cat_total in category_totals:
        cat_total_float = float(cat_total)
        percentage = (cat_total_float / total_expenses * 100) if total_expenses > 0 else 0.0
        breakdown.append(
            CategoryBreakdown(
                category_name=cat_name,
                total=round(cat_total_float, 2),
                percentage=round(percentage, 1),
            )
        )

    # Sort by total descending
    breakdown.sort(key=lambda x: x.total, reverse=True)

    return MonthlySummary(
        month=f"{year}-{month:02d}",
        total_income=round(total_income, 2),
        total_expenses=round(total_expenses, 2),
        net_savings=round(total_income - total_expenses, 2),
        category_breakdown=breakdown,
    )
