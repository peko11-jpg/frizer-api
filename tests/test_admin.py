from app.models import Role

SERVICE = {"name": "Šišanje", "duration_minutes": 30, "price": 8}


def test_duplicate_service_name_rejected(client, make_user):
    _, admin_h = make_user("admin@test.com", Role.admin)
    assert client.post("/services", json=SERVICE, headers=admin_h).status_code == 201
    r = client.post("/services", json={**SERVICE, "name": "šišanje"}, headers=admin_h)
    assert r.status_code == 409


def test_admin_can_change_role(client, make_user):
    _, admin_h = make_user("admin@test.com", Role.admin)
    user, _ = make_user("frizer@test.com", Role.client)
    r = client.patch(f"/users/{user.id}/role", json={"role": "stylist"}, headers=admin_h)
    assert r.status_code == 200
    assert r.json()["role"] == "stylist"


def test_client_cannot_change_role(client, make_user):
    _, client_h = make_user("klijent@test.com", Role.client)
    other, _ = make_user("drugi@test.com", Role.client)
    r = client.patch(f"/users/{other.id}/role", json={"role": "admin"}, headers=client_h)
    assert r.status_code == 403


def test_admin_cannot_change_own_role(client, make_user):
    admin, admin_h = make_user("admin@test.com", Role.admin)
    r = client.patch(f"/users/{admin.id}/role", json={"role": "client"}, headers=admin_h)
    assert r.status_code == 400