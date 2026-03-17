# backend/core/security.py

from passlib.context import CryptContext

# Password hashing context using bcrypt (industry standard)
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

# -------------------------
# HASH PASSWORD
# -------------------------
def hash_password(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    Returns a secure hashed password string.
    """
    return pwd_context.hash(password)

# -------------------------
# VERIFY PASSWORD
# -------------------------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a stored bcrypt hash.
    Returns True if match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)
