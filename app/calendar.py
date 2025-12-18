from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.bills import Bill
from app.schemas import BillCreate, BillUpdate, BillOut

router = APIRouter(prefix="/bills", tags=["Bills"])


# --------------------------------------------------
# GET — list active bills
# --------------------------------------------------
@router.get("", response_model=list[BillOut])
def list_bills(db: Session = Depends(get_db)):
    return (
        db.query(Bill)
        .filter(Bill.active.is_(True))
        .order_by(Bill.due_date.asc())
        .all()
    )


# --------------------------------------------------
# POST — create bill (rule only)
# --------------------------------------------------
@router.post("", response_model=BillOut)
def create_bill(payload: BillCreate, db: Session = Depends(get_db)):
    bill = Bill(
        name=payload.name,
        due_date=payload.due_date,
        amount=payload.amount,
        frequency=payload.frequency,   # recurrence rule
        category=payload.category,
        gst_credit=payload.gst_credit,
        notes=payload.notes,
        active=True,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill


# --------------------------------------------------
# PUT — update bill
# --------------------------------------------------
@router.put("/{bill_id}", response_model=BillOut)
def update_bill(
    bill_id: int,
    payload: BillUpdate,
    db: Session = Depends(get_db),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    # Apply only provided fields
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(bill, field, value)

    db.commit()
    db.refresh(bill)
    return bill


# --------------------------------------------------
# DELETE — soft delete bill
# --------------------------------------------------
@router.delete("/{bill_id}")
def remove_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.active = False
    db.commit()

    return {"status": "removed"}
