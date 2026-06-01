"""Pydantic schemas for budgets."""

import datetime as dt
from pydantic import BaseModel, Field


class BudgetBase(BaseModel):
    category_id: int
    amount: float = Field(..., gt=0, description="Monthly spending limit")
    month: str = Field(..., pattern=r"^\d{4}-\d{2}$", description="Month in YYYY-MM format")


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    user_id: int
    category_name: str
    created_at: dt.datetime

    class Config:
        from_attributes = True


class CategoryBudgetProgress(BaseModel):
    category_id: int
    category_name: str
    amount_spent: float
    budget_limit: float
    percentage_used: float
