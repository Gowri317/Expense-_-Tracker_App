"""
Database initialization: create tables and seed default categories.
"""

from backend.app.db.database import engine
from backend.app.db.base import Base

# Import all models so they register with Base.metadata
from backend.app.models.user import User  # noqa: F401
from backend.app.models.category import Category  # noqa: F401
from backend.app.models.expense import Expense  # noqa: F401
from backend.app.models.income import Income  # noqa: F401
from backend.app.models.budget import Budget  # noqa: F401


DEFAULT_CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Entertainment",
    "Shopping",
    "Health",
    "Education",
    "Other",
]


def init_db():
    """Create all tables and seed default categories if they don't exist."""
    Base.metadata.create_all(bind=engine)

    # Seed default categories
    from backend.app.db.database import SessionLocal

    db = SessionLocal()
    try:
        existing = db.query(Category).filter(Category.user_id.is_(None)).count()
        if existing == 0:
            for name in DEFAULT_CATEGORIES:
                db.add(Category(name=name, user_id=None))
            db.commit()
    finally:
        db.close()
