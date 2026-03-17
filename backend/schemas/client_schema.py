# backend/schemas/client_schema.py

from pydantic import BaseModel
from typing import Optional


class ClientCreate(BaseModel):
    name: str
    address: Optional[str] = None
    scope_of_work: Optional[dict] = None   # JSON-like dict
    rotation_order: Optional[int] = 0


class ClientUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    scope_of_work: Optional[dict] = None
    rotation_order: Optional[int] = None


class ClientOut(BaseModel):
    id: int
    name: str
    address: Optional[str]
    scope_of_work: Optional[dict]
    rotation_order: int

    class Config:
        orm_mode = True
