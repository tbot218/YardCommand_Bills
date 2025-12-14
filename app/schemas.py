from datetime import date
from typing import Optional
from pydantic import BaseModel


# -----------------------------
# Create (POST /bills)
# -----------------------------
class BillCreate(BaseModel):
    name: str
    due_date: date
    amount: float
    frequency: str              # monthly / quarterly / annual
    category: str = "business"  # business / personal
    gst_credit: bool = True
    notes: str = ""


# -----------------------------
# Update (PUT /bills/{id})
# All fields optional for safe partial updates
# -----------------------------
class BillUpdate(BaseModel):
    name: Optional[str] = None
    due_date: Optional[date] = None
    amount: Optional[float] = None
    frequency: Optional[str] = None
    category: Optional[str] = None
    gst_credit: Optional[bool] = None
    notes: Optional[str] = None


# -----------------------------
# Output (responses)
# -----------------------------
class BillOut(BillCreate):
    id: int
    active: bool

    class Config:
        from_attributes = True
