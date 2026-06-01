"""
Category API routes: list and create custom categories.
All routes require authentication.
"""

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.core.security import get_current_user
from backend.app.models.user import User
from backend.app.schemas.category import CategoryCreate, CategoryResponse
from backend.app.services.category_service import get_categories, create_category

router = APIRouter(prefix="/api/categories", tags=["Categories"])


@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return list of all categories (defaults + user's custom ones)."""
    return get_categories(db, current_user.id)


@router.post("/", response_model=CategoryResponse, status_code=201)
def add_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a custom category for the logged-in user."""
    return create_category(db, category_data, current_user.id)
