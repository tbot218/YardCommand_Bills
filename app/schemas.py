from datetime import date
from pydantic import BaseModel
from typing import Optional


class BillCreate(BaseModel):
    name: str
    due_date: date
    amount: float
    frequency: str = "monthly"
    category: str = "business"
    gst_credit: bool = True
    notes: str = ""

    # recurrence flags (v1 simple)
    repeat_monthly: bool = False
    repeat_4weeks: bool = False


class BillUpdate(BaseModel):
    name: Optional[str] = None
    due_date: Optional[date] = None
    amount: Optional[float] = None
    frequency: Optional[str] = None
    category: Optional[str] = None
    gst_credit: Optional[bool] = None
    notes: Optional[str] = None


class BillOut(BillCreate):
    id: int
    active: bool

    class Config:
        from_attributes = True
