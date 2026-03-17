# backend/api/schemas_client.py

from pydantic import BaseModel
from typing import Optional, Dict

# -----------------------------
# CLIENT CREATE SCHEMA
# -----------------------------
class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    scope_of_work: Optional[Dict[str, bool]] = None


# -----------------------------
# CLIENT UPDATE SCHEMA
# -----------------------------
class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    scope_of_work: Optional[Dict[str, bool]] = None
    rotation_order: Optional[int] = None


# -----------------------------
# CLIENT RESPONSE SCHEMA
# -----------------------------
class ClientResponse(BaseModel):
    id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    scope_of_work: Optional[Dict[str, bool]]
    rotation_order: int
    is_archived: bool

    class Config:
        from_attributes = True


# -----------------------------
# USER AUTH SCHEMAS
# -----------------------------
class UserRegister(BaseModel):
    username: str
    full_name: str
    password: str


class UserLogin(BaseModel):
    username: str
    password: str
