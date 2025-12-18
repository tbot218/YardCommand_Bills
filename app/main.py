print(">>> CONFIRMED: YardCommand_Bills app/main.py is running <<<")

from datetime import date, timedelta
from typing import Optional

from fastapi import FastAPI, Depends, Request, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from dateutil.relativedelta import relativedelta

from app.bills import Bill, Base
from app.database import engine, get_db
from app.schemas import BillCreate, BillUpdate, BillOut
from app.recurrence import expand_bills_to_instances
from app.totals import compute_weekly_totals, compute_monthly_totals


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
@app.get("/bills", response_model=list[BillOut])
def list_bills(db: Session = Depends(get_db)):
    return (
        db.query(Bill)
        .filter(Bill.active == True)
        .order_by(Bill.due_date.asc())
        .all()
    )


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

    # First bill
    create_one(payload.due_date)

    # Monthly recurrence
    if payload.repeat_monthly:
        for i in range(1, 12):
            create_one(payload.due_date + relativedelta(months=i))

    # 4-week recurrence
    elif payload.repeat_4weeks:
        d = payload.due_date
        for _ in range(1, 13):
            d += timedelta(days=28)
            create_one(d)

    db.commit()
    return created


@app.put("/bills/{bill_id}", response_model=BillOut)
def update_bill(
    bill_id: int,
    payload: BillUpdate,
    db: Session = Depends(get_db),
):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    for field, value in payload.dict(exclude_unset=True).items():
        setattr(bill, field, value)

    db.commit()
    db.refresh(bill)
    return bill


@app.delete("/bills/{bill_id}")
def remove_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()

    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")

    bill.active = False
    db.commit()
    return {"status": "removed"}


# --------------------------------------------------
# Helpers
# --------------------------------------------------
def _load_active_bills(db: Session):
    bills = (
        db.query(Bill)
        .filter(Bill.active == True)
        .all()
    )

    return [
        {
            "id": b.id,
            "amount": float(b.amount),
            "recurrence": b.frequency,
            "start_date": b.due_date,
            "user": "default",
        }
        for b in bills
    ]


# --------------------------------------------------
# API — Totals (VIEW-DRIVEN, FIXED)
# --------------------------------------------------
@app.get("/totals/weekly")
def get_weekly_totals(
    view_date: Optional[str] = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
):
    ref_date = date.fromisoformat(view_date) if view_date else date.today()

    start = ref_date - timedelta(days=30)
    end = ref_date + timedelta(days=90)

    bills = _load_active_bills(db)
    instances = expand_bills_to_instances(bills, start, end)
    totals = compute_weekly_totals(instances)

    year, week, _ = ref_date.isocalendar()
    current_key = f"{year}-W{week:02d}"

    return {
        "current_week": current_key,
        "totals": totals,
    }


@app.get("/totals/monthly")
def get_monthly_totals(
    view_date: Optional[str] = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
):
    ref_date = date.fromisoformat(view_date) if view_date else date.today()

    start = ref_date.replace(day=1)
    end = ref_date + relativedelta(months=3)

    bills = _load_active_bills(db)
    instances = expand_bills_to_instances(bills, start, end)
    totals = compute_monthly_totals(instances)

    current_key = f"{ref_date.year}-{ref_date.month:02d}"

    return {
        "current_month": current_key,
        "totals": totals,
    }
