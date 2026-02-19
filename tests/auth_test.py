from src.constants.constants import (
    AUTH_REGISTER_COMPLETE_ENDPOINT,
    AUTH_GET_TOKEN_COMPLETE_ENDPOINT,
)
from src.models.users import User
from src.routers.api.auth.utils import get_password_hash


def test_auth_register_user(client, fake):
    new_user = {
        "username": fake.user_name(),
        "password": fake.password(),
    }

    response = client.post(AUTH_REGISTER_COMPLETE_ENDPOINT, json=new_user)

    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == new_user["username"]
    assert data["bank_account"]["account_type"] == "personal"


def test_auth_get_token(client, session, fake):
    login_data = {
        "username": fake.user_name(),
        "password": fake.password(),
    }

    new_user = User(
        email=fake.email(),
        username=login_data["username"],
        full_name=fake.name(),
        disabled=False,
        hashed_password=get_password_hash(login_data["password"]),
    )

    session.add(new_user)
    session.commit()

    response = client.post(AUTH_GET_TOKEN_COMPLETE_ENDPOINT, data=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
