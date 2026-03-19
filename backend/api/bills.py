from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas_bill import BillCreate, BillResponse, BillUpdate
from backend.db import models
from backend.db.database import get_db

router = APIRouter()


def get_default_client(db: Session) -> models.Client:
    client = (
        db.query(models.Client)
        .filter(models.Client.name == "General Bills")
        .first()
    )
    if client:
        return client

    client = models.Client(
        name="General Bills",
        address=None,
        scope_of_work=None,
        rotation_order=0,
        is_archived=False,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def bill_to_response(db_bill: models.Bill) -> BillResponse:
    return BillResponse(
        id=db_bill.id,
        client_id=db_bill.client_id,
        client_name=db_bill.client.name if db_bill.client else "General Bills",
        title=db_bill.title,
        description=db_bill.description,
        issue_date=db_bill.issue_date,
        due_date=db_bill.due_date,
        amount=db_bill.amount_cents / 100,
        status=db_bill.status,
        paid_at=db_bill.paid_at,
        created_at=db_bill.created_at,
    )


@router.get("/", response_model=list[BillResponse])
def list_bills(
    client_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Bill).join(models.Client)

    if client_id is not None:
        query = query.filter(models.Bill.client_id == client_id)

    if status:
        query = query.filter(models.Bill.status == status)

    bills = query.order_by(models.Bill.due_date.asc(), models.Bill.id.desc()).all()
    return [bill_to_response(bill) for bill in bills]


@router.post("/", response_model=BillResponse)
def create_bill(
    payload: BillCreate,
    db: Session = Depends(get_db),
):
    if payload.client_id is None:
        client = get_default_client(db)
    else:
        client = db.query(models.Client).filter(models.Client.id == payload.client_id).first()
        if not client:
            raise HTTPException(status_code=404, detail="Client not found.")

    if payload.due_date < payload.issue_date:
        raise HTTPException(status_code=400, detail="Due date cannot be before issue date.")

    bill = models.Bill(
        client_id=client.id,
        title=payload.title,
        description=payload.description,
        issue_date=payload.issue_date,
        due_date=payload.due_date,
        amount_cents=round(payload.amount * 100),
        status=payload.status,
    )

    db.add(bill)
    db.commit()
    db.refresh(bill)

    return bill_to_response(bill)


@router.put("/{bill_id}", response_model=BillResponse)
def update_bill(
    bill_id: int,
    payload: BillUpdate,
    db: Session = Depends(get_db),
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found.")

    next_issue_date = payload.issue_date or bill.issue_date
    next_due_date = payload.due_date or bill.due_date
    if next_due_date < next_issue_date:
        raise HTTPException(status_code=400, detail="Due date cannot be before issue date.")

    if payload.title is not None:
        bill.title = payload.title

    if payload.description is not None:
        bill.description = payload.description

    if payload.issue_date is not None:
        bill.issue_date = payload.issue_date

    if payload.due_date is not None:
        bill.due_date = payload.due_date

    if payload.amount is not None:
        bill.amount_cents = round(payload.amount * 100)

    if payload.status is not None:
        bill.status = payload.status

    db.commit()
    db.refresh(bill)

    return bill_to_response(bill)


@router.delete("/{bill_id}")
def delete_bill(
    bill_id: int,
    db: Session = Depends(get_db),
):
    bill = db.query(models.Bill).filter(models.Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found.")

    db.delete(bill)
    db.commit()

    return {"status": "deleted", "id": bill_id}
