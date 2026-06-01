"""
Category service: list and create custom categories.
"""

from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status

from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate


def get_categories(db: Session, user_id: int) -> List[Category]:
    """Get all categories available to a user (defaults + user's custom ones)."""
    return (
        db.query(Category)
        .filter(or_(Category.user_id.is_(None), Category.user_id == user_id))
        .order_by(Category.name)
        .all()
    )


def create_category(db: Session, category_data: CategoryCreate, user_id: int) -> Category:
    """Create a custom category for a user. Prevents duplicates."""
    existing = (
        db.query(Category)
        .filter(
            Category.name == category_data.name,
            or_(Category.user_id.is_(None), Category.user_id == user_id),
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Category '{category_data.name}' already exists",
        )

    category = Category(name=category_data.name, user_id=user_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category
