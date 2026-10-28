from datetime import datetime, timedelta

from app.models import Role


def future(hour, minute=0):
    day = datetime.now() + timedelta(days=7)
    return day.replace(hour=hour, minute=minute, second=0, microsecond=0).isoformat()


def setup_salon(client, make_user):
    admin, admin_h = make_user("admin@test.com", Role.admin)
    stylist, _ = make_user("frizer@test.com", Role.stylist)
    _, client_h = make_user("klijent@test.com", Role.client)
    r = client.post(
        "/services",
        json={"name": "Šišanje", "duration_minutes": 30, "price": 8},
        headers=admin_h,
    )
    return stylist.id, r.json()["id"], client_h


def test_client_cannot_create_service(client, make_user):
    _, headers = make_user("klijent@test.com", Role.client)
    r = client.post(
        "/services",
        json={"name": "Šišanje", "duration_minutes": 30, "price": 8},
        headers=headers,
    )
    assert r.status_code == 403


def test_booking_created(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    r = client.post(
        "/bookings",
        json={"stylist_id": stylist_id, "service_id": service_id, "start_time": future(10)},
        headers=headers,
    )
    assert r.status_code == 201


def test_double_booking_rejected(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    body = {"stylist_id": stylist_id, "service_id": service_id, "start_time": future(10)}
    assert client.post("/bookings", json=body, headers=headers).status_code == 201
    assert client.post("/bookings", json=body, headers=headers).status_code == 409


def test_overlapping_booking_rejected(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    first = {"stylist_id": stylist_id, "service_id": service_id, "start_time": future(10)}
    overlap = {**first, "start_time": future(10, 15)}
    client.post("/bookings", json=first, headers=headers)
    assert client.post("/bookings", json=overlap, headers=headers).status_code == 409


def test_cancelled_slot_can_be_rebooked(client, make_user):
    stylist_id, service_id, headers = setup_salon(client, make_user)
    body = {"stylist_id": stylist_id, "service_id": service_id, "start_time": future(10)}
    booking_id = client.post("/bookings", json=body, headers=headers).json()["id"]
    client.patch(f"/bookings/{booking_id}/cancel", headers=headers)
    assert client.post("/bookings", json=body, headers=headers).status_code == 201