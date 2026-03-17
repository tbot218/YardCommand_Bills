from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class BillCreate(BaseModel):
    client_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    issue_date: date
    due_date: date
    amount: float = Field(gt=0)
    status: str = "draft"


class BillUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    amount: Optional[float] = Field(default=None, gt=0)
    status: Optional[str] = None


class BillResponse(BaseModel):
    id: int
    client_id: Optional[int]
    client_name: str
    title: str
    description: Optional[str]
    issue_date: date
    due_date: date
    amount: float
    status: str
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
