from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.bills import Bill, Base
from app.database import engine, get_db
from app.schemas import BillCreate, BillOut

app = FastAPI(title="Yard Command – Bills Calendar")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

Base.metadata.create_all(bind=engine)

@app.get("/calendar", response_class=HTMLResponse)
def calendar_view(request: Request):
    return templates.TemplateResponse(
        "calendar.html",
        {"request": request}
    )

@app.post("/bills", response_model=BillOut)
def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    new_bill = Bill(**bill.model_dump(), active=True)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return new_bill

@app.get("/bills", response_model=list[BillOut])
def list_bills(db: Session = Depends(get_db)):
    return db.query(Bill).filter(Bill.active == True).all()
