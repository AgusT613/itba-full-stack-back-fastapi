import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
from src.db.connection import get_session
from faker import Faker
from src.main import app
from .utils import _create_user


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    with Session(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="fake")
def fake_fixture():
    return Faker()


@pytest.fixture(name="client_auth")
def client_auth_fixture(client, fake, session):
    def _client_auth(username=None, password=None):
        username = username or fake.user_name()
        password = password or fake.password()

        user = _create_user(session, username=username, password=password, fake=fake)

        response = client.post(
            "/api/auth/token",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        assert response.status_code == 200
        token = response.json().get("access_token")
        client.headers.update({"Authorization": f"Bearer {token}"})

        return client, user

    return _client_auth
