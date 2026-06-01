"""Pydantic schemas for categories."""

import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Groceries"])


class CategoryResponse(BaseModel):
    id: int
    name: str
    user_id: Optional[int] = None
    created_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True
