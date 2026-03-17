# backend/core/auth_dependency.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from backend.core.jwt_handler import verify_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_access_token(token)

    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    return payload  # contains user_id, username, role
