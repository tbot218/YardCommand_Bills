# backend/core/jwt_handler.py

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

# SECRET KEY — generate one for production
SECRET_KEY = "YARD_COMMAND_SECRET_KEY_CHANGE_ME"
ALGORITHM = "HS256"

# Weekly token validity
ACCESS_TOKEN_EXPIRE_DAYS = 7


# ---------------------------------------------------
# CREATE JWT TOKEN
# ---------------------------------------------------
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ---------------------------------------------------
# VERIFY JWT TOKEN
# ---------------------------------------------------
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains user data
    except JWTError:
        return None
