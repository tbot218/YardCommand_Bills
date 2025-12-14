from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from app.bills import Bill, Base
from app.database import engine, get_db
from app.schemas import BillCreate, BillUpdate, BillOut


# --------------------------------------------------
# App setup
# --------------------------------------------------
app = FastAPI(title="Yard Command – Bills Calendar")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# Views
# --------------------------------------------------
@app.get("/calendar", response_class=HTMLResponse)
def calendar_view(request: Request):
    return templates.TemplateResponse(
        "calendar.html",
        {"request": request},
    )


# --------------------------------------------------
# API — Bills
# --------------------------------------------------

# GET — all active bills
@app.get("/bills", response_model=list[BillOut])
def list_bills(db: Session = Depends(get_db)):
    return (
        db.query(Bill)
        .filter(Bill.active == True)
        .order_by(Bill.due_date.asc())
        .all()
    )


# POST — create bill (+ optional recurrence)
@app.post("/bills", response_model=list[BillOut])
def create_bill(payload: BillCreate, db: Session = Depends(get_db)):
    created: list[Bill] = []

    def create_one(due_date):
        bill = Bill(
            name=payload.name,
            due_date=due_date,
            amount=payload.amount,
            frequency=payload.frequency,
            category=payload.category,
            gst_credit=payload.gst_credit,
            notes=payload.notes,
            active=True,
        )
        db.add(bill)
        db.flush()
        created.append(bill)

    # Always create the first bill
    create_one(payload.due_date)

    # Recurrence: same date every month (12 months total)
    if payload.repeat_monthly:
        for i in range(1, 12):
            create_one(payload.due_date + relativedelta(months=i))

    # Recurrence: every 4 weeks (28-day cadence)
    elif payload.repeat_4weeks:
        d = payload.due_date
        for _ in range(1, 13):
            d = d + timedelta(days=28)
            create_one(d)

    db.commit()
    return created


# PUT — update bill (Save button)
@app.put("/bills/{bill_id}", response_model=BillOut)
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


# DELETE — remove bill (soft delete)
@app.delete("/bills/{bill_id}")
def remove_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.active = False
    db.commit()

    return {"status": "removed"}
