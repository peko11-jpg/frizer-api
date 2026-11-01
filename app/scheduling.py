from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking, BookingStatus

WORK_START = time(9, 0)
WORK_END = time(17, 0)
SLOT_STEP = timedelta(minutes=30)   # termini se nude na svakih 30 min
CLOSED_WEEKDAYS = {6}               # 0 = ponedjeljak ... 6 = nedjelja


def is_within_working_hours(start: datetime, end: datetime) -> bool:
    if start.weekday() in CLOSED_WEEKDAYS:
        return False
    if start.date() != end.date():   # ne smije preći u sljedeći dan
        return False
    return WORK_START <= start.time() and end.time() <= WORK_END


def free_slots(
    db: Session, stylist_id: int, day: date, duration_minutes: int
) -> list[datetime]:
    if day.weekday() in CLOSED_WEEKDAYS:
        return []

    duration = timedelta(minutes=duration_minutes)
    opening = datetime.combine(day, WORK_START)
    closing = datetime.combine(day, WORK_END)

    # sve aktivne rezervacije tog frizera koje diraju taj dan
    booked = db.scalars(
        select(Booking).where(
            Booking.stylist_id == stylist_id,
            Booking.status == BookingStatus.booked,
            Booking.start_time < closing,
            Booking.end_time > opening,
        )
    ).all()

    slots = []
    current = opening
    now = datetime.now()
    while current + duration <= closing:
        end = current + duration
        is_busy = any(b.start_time < end and b.end_time > current for b in booked)
        if not is_busy and current > now:
            slots.append(current)
        current += SLOT_STEP
    return slots