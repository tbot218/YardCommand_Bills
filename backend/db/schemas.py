# backend/db/schemas.py

from pydantic import BaseModel

# -------------------------
# REGISTER MODEL
# -------------------------
class UserRegister(BaseModel):
    username: str
    full_name: str
    password: str


# -------------------------
# LOGIN MODEL
# -------------------------
class UserLogin(BaseModel):
    username: str
    password: str
