from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, Service, User
from app.schemas import StylistOut
from app.scheduling import free_slots

router = APIRouter(prefix="/stylists", tags=["stylists"])


@router.get("", response_model=list[StylistOut])
def list_stylists(db: Session = Depends(get_db)):
    return db.scalars(
        select(User).where(User.role == Role.stylist).order_by(User.full_name)
    ).all()


@router.get("/{stylist_id}/availability", response_model=list[datetime])
def availability(
    stylist_id: int,
    service_id: int,
    day: date = Query(alias="date"),
    db: Session = Depends(get_db),
):
    stylist = db.get(User, stylist_id)
    if stylist is None or stylist.role != Role.stylist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Frizer ne postoji")

    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usluga ne postoji")

    return free_slots(db, stylist.id, day, service.duration_minutes)