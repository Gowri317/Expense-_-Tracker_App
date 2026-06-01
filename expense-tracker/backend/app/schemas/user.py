"""Pydantic schemas for user registration, login, and token responses."""

import datetime as dt
from typing import Optional
from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, examples=["john_doe"])
    password: str = Field(..., min_length=6, max_length=100, examples=["secure123"])


class UserResponse(BaseModel):
    id: int
    username: str
    created_at: Optional[dt.datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None
