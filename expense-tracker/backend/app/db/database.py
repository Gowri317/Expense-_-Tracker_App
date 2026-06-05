"""
Database engine, session factory, and get_db dependency.
Supports both SQLite and PostgreSQL via DATABASE_URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Render provides postgres:// but SQLAlchemy 2.x requires postgresql://
database_url = settings.DATABASE_URL
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

logger.info(f"Database URL scheme: {database_url.split('://')[0] if '://' in database_url else 'unknown'}")

# Handle SQLite-specific connect args
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    database_url,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True,  # Auto-detect stale connections
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: yield a DB session, close it when done."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
