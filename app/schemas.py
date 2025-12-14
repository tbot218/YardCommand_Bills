from datetime import date
from pydantic import BaseModel


class BillCreate(BaseModel):
    name: str
    due_date: date
    amount: float
    frequency: str              # monthly / quarterly / annual
    category: str = "business"  # business / personal
    gst_credit: bool = True
    notes: str = ""


class BillOut(BillCreate):
    id: int
    active: bool

    class Config:
        from_attributes = True
