def test_register_and_login(client):
    r = client.post(
        "/auth/register",
        json={"email": "a@test.com", "password": "lozinka123", "full_name": "A"},
    )
    assert r.status_code == 201
    assert r.json()["role"] == "client"
    assert "hashed_password" not in r.json()

    r = client.post("/auth/login", data={"username": "a@test.com", "password": "lozinka123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_duplicate_email_rejected(client):
    body = {"email": "a@test.com", "password": "lozinka123", "full_name": "A"}
    client.post("/auth/register", json=body)
    assert client.post("/auth/register", json=body).status_code == 409


def test_wrong_password_rejected(client, make_user):
    make_user("a@test.com")
    r = client.post("/auth/login", data={"username": "a@test.com", "password": "pogresna123"})
    assert r.status_code == 401


def test_me_requires_token(client):
    assert client.get("/auth/me").status_code == 401