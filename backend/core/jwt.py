from datetime import datetime, timedelta
from jose import JWTError, jwt

# -----------------------------
# JWT CONFIG
# -----------------------------
SECRET_KEY = "your_super_secret_key_change_this"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7  # Weekly expiry


# -----------------------------
# CREATE TOKEN
# -----------------------------
def create_access_token(data: dict):
    """Attach expiry and return signed JWT token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# -----------------------------
# VERIFY TOKEN
# -----------------------------
def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # contains user_id, username, role, exp
    except JWTError:
        return None
