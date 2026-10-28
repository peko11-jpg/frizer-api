from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Role, User
from app.schemas import StylistOut

router = APIRouter(prefix="/stylists", tags=["stylists"])


@router.get("", response_model=list[StylistOut])
def list_stylists(db: Session = Depends(get_db)):
    return db.scalars(
        select(User).where(User.role == Role.stylist).order_by(User.full_name)
    ).all()