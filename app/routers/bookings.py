from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Booking, BookingStatus, Role, Service, User
from app.schemas import BookingCreate, BookingOut
from app.scheduling import is_within_working_hours

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stylist = db.get(User, data.stylist_id)
    if stylist is None or stylist.role != Role.stylist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Frizer ne postoji")
    if stylist.id == current_user.id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Ne možeš zakazati kod sebe")

    service = db.get(Service, data.service_id)
    if service is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usluga ne postoji")

    if data.start_time <= datetime.now():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Termin mora biti u budućnosti")

    end_time = data.start_time + timedelta(minutes=service.duration_minutes)
    if not is_within_working_hours(data.start_time, end_time):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Salon ne radi u tom terminu (radno vrijeme 09:00-17:00, nedjeljom zatvoreno)",
        )

    # Preklapanje: postojeći termin počinje prije nego što novi završi
    # I završava poslije nego što novi počne
    conflict = db.scalar(
        select(Booking).where(
            Booking.stylist_id == stylist.id,
            Booking.status == BookingStatus.booked,
            Booking.start_time < end_time,
            Booking.end_time > data.start_time,
        )
    )
    if conflict:
        raise HTTPException(status.HTTP_409_CONFLICT, "Frizer je zauzet u tom terminu")

    booking = Booking(
        client_id=current_user.id,
        stylist_id=stylist.id,
        service_id=service.id,
        start_time=data.start_time,
        end_time=end_time,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/my", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    query = select(Booking).order_by(Booking.start_time)
    if current_user.role == Role.client:
        query = query.where(Booking.client_id == current_user.id)
    elif current_user.role == Role.stylist:
        query = query.where(Booking.stylist_id == current_user.id)
    # admin vidi sve
    return db.scalars(query).all()


@router.patch("/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Rezervacija ne postoji")

    allowed = current_user.role == Role.admin or current_user.id in (
        booking.client_id,
        booking.stylist_id,
    )
    if not allowed:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Nemaš dozvolu za ovu akciju")

    booking.status = BookingStatus.cancelled
    db.commit()
    db.refresh(booking)
    return booking