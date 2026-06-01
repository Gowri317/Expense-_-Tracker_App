"""Pydantic schemas for income CRUD operations."""

import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field


class IncomeCreate(BaseModel):
    amount: float = Field(..., gt=0, examples=[3000.00])
    source: str = Field(..., min_length=1, max_length=200, examples=["Freelance"])
    date: dt.date = Field(default_factory=dt.date.today)


class IncomeUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    source: Optional[str] = Field(None, min_length=1, max_length=200)
    date: Optional[dt.date] = None


class IncomeResponse(BaseModel):
    id: int
    amount: float
    source: str
    date: dt.date
    user_id: int
    created_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
