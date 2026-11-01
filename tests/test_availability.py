from datetime import date, timedelta

from tests.test_bookings import future, setup_salon


def test_booking_outside_working_hours_rejected(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    base = {"stylist_id": stylist_id, "service_id": service_id}

    too_early = client.post("/bookings", json={**base, "start_time": future(7)}, headers=headers)
    too_late = client.post("/bookings", json={**base, "start_time": future(16, 45)}, headers=headers)
    assert too_early.status_code == 400
    assert too_late.status_code == 400   # završilo bi u 17:15


def test_booking_until_closing_time_allowed(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    r = client.post(
        "/bookings",
        json={"stylist_id": stylist_id, "service_id": service_id, "start_time": future(16, 30)},
        headers=headers,
    )
    assert r.status_code == 201   # 16:30 + 30 min = tačno 17:00


def test_availability_lists_free_slots(client, make_user):
    stylist_id, service_id, _ = setup_salon(client, make_user)
    day = future(10)[:10]
    url = f"/stylists/{stylist_id}/availability?date={day}&service_id={service_id}"
    slots = client.get(url).json()
    assert len(slots) == 16   # od 09:00 do 16:30, svakih 30 min


def test_booked_slot_disappears_from_availability(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    client.post(
        "/bookings",
        json={"stylist_id": stylist_id, "service_id": service_id, "start_time": future(10)},
        headers=headers,
    )
    day = future(10)[:10]
    url = f"/stylists/{stylist_id}/availability?date={day}&service_id={service_id}"
    slots = client.get(url).json()
    assert f"{day}T10:00:00" not in slots
    assert len(slots) == 15


def test_closed_on_sunday(client, make_user):
    stylist_id, service_id, _ = setup_salon(client, make_user)
    today = date.today()
    sunday = today + timedelta(days=(6 - today.weekday()) % 7)
    url = f"/stylists/{stylist_id}/availability?date={sunday}&service_id={service_id}"
    assert client.get(url).json() == []
    