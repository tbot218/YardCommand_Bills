print(">>> CONFIRMED: YardCommand_Bills app/main.py is running <<<")
from fastapi import FastAPI, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date, timedelta

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

    # Always create first bill
    create_one(payload.due_date)

    # Monthly recurrence (12 months)
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
# API — Totals (Phase 3)
# --------------------------------------------------

def _load_active_bills(db: Session):
    """
    Convert Bill ORM rows into recurrence-compatible dicts.
    """
    bills = (
        db.query(Bill)
        .filter(Bill.active == True)
        .all()
    )

    return [
        {
            "id": b.id,
            "amount": float(b.amount),
            "recurrence": b.frequency,   # string or dict
            "start_date": b.due_date,
            "user": "default",           # future-ready
        }
        for b in bills
    ]


@app.get("/totals/weekly")
def get_weekly_totals(db: Session = Depends(get_db)):
    today = date.today()
    start = today - timedelta(days=30)
    end = today + timedelta(days=90)

    bills = _load_active_bills(db)
    instances = expand_bills_to_instances(bills, start, end)
    totals = compute_weekly_totals(instances)

    year, week, _ = today.isocalendar()
    current_key = f"{year}-W{week:02d}"

    return {
        "current_week": current_key,
        "totals": totals,
    }


@app.get("/totals/monthly")
def get_monthly_totals(db: Session = Depends(get_db)):
    today = date.today()
    start = today.replace(day=1)
    end = today + relativedelta(months=3)

    bills = _load_active_bills(db)
    instances = expand_bills_to_instances(bills, start, end)
    totals = compute_monthly_totals(instances)

    current_key = f"{today.year}-{today.month:02d}"

    return {
        "current_month": current_key,
        "totals": totals,
    }
