import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, ForeignKey, DateTime, Enum, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Role(str, enum.Enum):
    client = "client"
    stylist = "stylist"
    admin = "admin"


class BookingStatus(str, enum.Enum):
    booked = "booked"
    cancelled = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(100))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.client)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    duration_minutes: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(8, 2))


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    stylist_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus), default=BookingStatus.booked
    )