"""Pydantic schemas for monthly summary endpoint."""

from typing import List
from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category_name: str
    total: float
    percentage: float


class MonthlySummary(BaseModel):
    month: str  # YYYY-MM
    total_income: float
    total_expenses: float
    net_savings: float
    category_breakdown: List[CategoryBreakdown]
