# backend/api/schemas_auth.py

from pydantic import BaseModel


class UserRegister(BaseModel):
    username: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
