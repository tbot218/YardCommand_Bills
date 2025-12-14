from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.bills import Bill
from app.schemas import BillCreate, BillUpdate, BillOut

router = APIRouter()
@router.get("/bills", response_model=list[BillOut])
def list_bills(db: Session = Depends(get_db)):
    return (
        db.query(Bill)
        .filter(Bill.active == True)
        .order_by(Bill.due_date.asc())
        .all()
    )
@router.post("/bills", response_model=BillOut)
def create_bill(payload: BillCreate, db: Session = Depends(get_db)):
    bill = Bill(
        name=payload.name,
        due_date=payload.due_date,
        amount=payload.amount,
        frequency=payload.frequency,
        category=payload.category,
        gst_credit=payload.gst_credit,
        notes=payload.notes,
        active=True,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)
    return bill
@router.put("/bills/{bill_id}", response_model=BillOut)
def update_bill(
    bill_id: int,
    payload: BillUpdate,
    db: Session = Depends(get_db),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    if payload.name is not None:
        bill.name = payload.name
    if payload.due_date is not None:
        bill.due_date = payload.due_date
    if payload.amount is not None:
        bill.amount = payload.amount
    if payload.frequency is not None:
        bill.frequency = payload.frequency
    if payload.category is not None:
        bill.category = payload.category
    if payload.gst_credit is not None:
        bill.gst_credit = payload.gst_credit
    if payload.notes is not None:
        bill.notes = payload.notes

    db.commit()
    db.refresh(bill)
    return bill
@router.delete("/bills/{bill_id}")
def remove_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.active = False
    db.commit()

    return {"status": "removed"}
