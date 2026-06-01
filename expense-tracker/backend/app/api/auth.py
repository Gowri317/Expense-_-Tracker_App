"""
Auth API routes: register and login.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.schemas.user import UserCreate, UserResponse, Token
from backend.app.services.auth_service import register_user, authenticate_user, create_user_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user with username and password."""
    user = register_user(db, user_data)
    return user


@router.post("/login", response_model=Token)
def login(user_data: UserCreate, db: Session = Depends(get_db)):
    """Login and receive a JWT access token."""
    user = authenticate_user(db, user_data.username, user_data.password)
    return create_user_token(user)
