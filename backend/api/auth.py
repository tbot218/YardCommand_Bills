from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db.database import get_db
from backend.db import models, schemas
from backend.core.security import hash_password, verify_password


# ==========================================================
#   ROUTER
# ==========================================================
router = APIRouter(
    tags=["Authentication"]
)


# ==========================================================
#   LOGIN (For your React Login page)
# ==========================================================
@router.post("/login")
def login_user(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    """
    Validates username + password.
    Returns user object temporarily (JWT coming soon).
    """

    user = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=400,
            detail="Invalid username or password."
        )

    # TODO: Replace with JWT later
    return {
        "status": "success",
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "role": user.role
        }
    }


# ==========================================================
#   REGISTER NEW USER (CREW or CEO)
# ==========================================================
@router.post("/register")
def register_user(payload: schemas.UserRegister, db: Session = Depends(get_db)):
    """
    Creates a new user account.
    Default role = crew (CEO can change later).
    """

    # Check if username exists
    existing_user = (
        db.query(models.User)
        .filter(models.User.username == payload.username)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already taken."
        )

    # Create user record
    new_user = models.User(
        username=payload.username,
        full_name=payload.full_name,
        password_hash=hash_password(payload.password),
        role="crew"  # default user role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "status": "success",
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "full_name": new_user.full_name,
            "role": new_user.role
        }
    }
