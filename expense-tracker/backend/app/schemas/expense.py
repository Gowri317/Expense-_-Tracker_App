"""Pydantic schemas for expense CRUD operations."""

import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    amount: float = Field(..., gt=0, examples=[25.50])
    category_id: int = Field(..., examples=[1])
    date: dt.date = Field(default_factory=dt.date.today)
    note: Optional[str] = Field(None, max_length=500, examples=["Lunch at cafe"])


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    date: Optional[dt.date] = None
    note: Optional[str] = Field(None, max_length=500)


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category_id: int
    category_name: Optional[str] = None
    date: dt.date
    note: Optional[str] = None
    user_id: int
    created_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
