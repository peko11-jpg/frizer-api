from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import BookingStatus, Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    full_name: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ServiceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    duration_minutes: int = Field(gt=0, le=480)
    price: Decimal = Field(ge=0)


class ServiceOut(ServiceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class StylistOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str


class BookingCreate(BaseModel):
    stylist_id: int
    service_id: int
    start_time: datetime

    @field_validator("start_time")
    @classmethod
    def no_timezone(cls, v: datetime) -> datetime:
        if v.tzinfo is not None:
            raise ValueError("Pošalji vrijeme bez vremenske zone, npr. 2026-11-02T10:00:00")
        return v


class BookingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    stylist_id: int
    service_id: int
    start_time: datetime
    end_time: datetime
    status: BookingStatus

class RoleUpdate(BaseModel):
    role: Role