import json
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.api.schemas_client import ClientCreate, ClientResponse, ClientUpdate
from backend.db import models
from backend.db.database import get_db

router = APIRouter()


def client_to_response(db_client: models.Client) -> ClientResponse:
    scope_dict = None
    if db_client.scope_of_work:
        try:
            scope_dict = json.loads(db_client.scope_of_work)
        except json.JSONDecodeError:
            scope_dict = None

    return ClientResponse(
        id=db_client.id,
        name=db_client.name,
        phone=db_client.phone,
        email=db_client.email,
        address=db_client.address,
        scope_of_work=scope_dict,
        rotation_order=db_client.rotation_order,
        is_archived=db_client.is_archived,
    )


@router.post("/", response_model=ClientResponse)
def create_client(
    payload: ClientCreate,
    db: Session = Depends(get_db),
):
    existing = (
        db.query(models.Client)
        .filter(models.Client.name == payload.name, models.Client.is_archived == False)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Client with this name already exists (not archived).",
        )

    scope_json: Optional[str] = None
    if payload.scope_of_work is not None:
        scope_json = json.dumps(payload.scope_of_work)

    new_client = models.Client(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        address=payload.address,
        scope_of_work=scope_json,
        rotation_order=0,
        is_archived=False,
    )

    db.add(new_client)
    db.commit()
    db.refresh(new_client)

    return client_to_response(new_client)


@router.get("/", response_model=List[ClientResponse])
def list_clients(
    include_archived: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.Client)
    if not include_archived:
        query = query.filter(models.Client.is_archived == False)

    clients = query.order_by(models.Client.rotation_order.asc(), models.Client.id.asc()).all()
    return [client_to_response(client) for client in clients]


@router.put("/{client_id}", response_model=ClientResponse)
def update_client(
    client_id: int,
    payload: ClientUpdate,
    db: Session = Depends(get_db),
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found.")

    if payload.name is not None:
        db_client.name = payload.name

    if payload.phone is not None:
        db_client.phone = payload.phone

    if payload.email is not None:
        db_client.email = payload.email

    if payload.address is not None:
        db_client.address = payload.address

    if payload.scope_of_work is not None:
        db_client.scope_of_work = json.dumps(payload.scope_of_work)

    if payload.rotation_order is not None:
        db_client.rotation_order = payload.rotation_order

    db.commit()
    db.refresh(db_client)

    return client_to_response(db_client)


@router.post("/{client_id}/archive", response_model=ClientResponse)
def archive_client(
    client_id: int,
    db: Session = Depends(get_db),
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found.")

    db_client.is_archived = True
    db.commit()
    db.refresh(db_client)

    return client_to_response(db_client)


@router.post("/{client_id}/unarchive", response_model=ClientResponse)
def unarchive_client(
    client_id: int,
    db: Session = Depends(get_db),
):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found.")

    db_client.is_archived = False
    db.commit()
    db.refresh(db_client)

    return client_to_response(db_client)
