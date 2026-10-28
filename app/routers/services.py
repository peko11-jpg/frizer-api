from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_role
from app.models import Role, Service
from app.schemas import ServiceCreate, ServiceOut

router = APIRouter(prefix="/services", tags=["services"])

admin_only = Depends(require_role(Role.admin))


@router.get("", response_model=list[ServiceOut])
def list_services(db: Session = Depends(get_db)):
    # javno: svako smije da vidi cjenovnik
    return db.scalars(select(Service).order_by(Service.name)).all()


@router.post("", response_model=ServiceOut, status_code=201, dependencies=[admin_only])
def create_service(data: ServiceCreate, db: Session = Depends(get_db)):
    service = Service(**data.model_dump())
    db.add(service)
    db.commit()
    db.refresh(service)
    return service


@router.put("/{service_id}", response_model=ServiceOut, dependencies=[admin_only])
def update_service(service_id: int, data: ServiceCreate, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usluga ne postoji")
    for field, value in data.model_dump().items():
        setattr(service, field, value)
    db.commit()
    db.refresh(service)
    return service


@router.delete("/{service_id}", status_code=204, dependencies=[admin_only])
def delete_service(service_id: int, db: Session = Depends(get_db)):
    service = db.get(Service, service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usluga ne postoji")
    db.delete(service)
    db.commit()