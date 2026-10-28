import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import Role, User

# privremena baza samo u memoriji, nestaje kad testovi završe
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine)


@pytest.fixture
def db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def make_user(client, db):
    """Pravi korisnika sa željenom ulogom i vraća (user, zaglavlje sa tokenom)."""

    def _make(email, role=Role.client, password="lozinka123"):
        client.post(
            "/auth/register",
            json={"email": email, "password": password, "full_name": email},
        )
        user = db.query(User).filter_by(email=email).one()
        user.role = role
        db.commit()
        resp = client.post(
            "/auth/login", data={"username": email, "password": password}
        )
        token = resp.json()["access_token"]
        return user, {"Authorization": f"Bearer {token}"}

    return _make