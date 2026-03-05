from src.models.accounts import BankAccount
from src.models.user_saved_aliases import UserSavedAlias
from sqlmodel import select
from fastapi import status


def test_get_all_aliases(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/alias/all")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for alias in data:
        assert "alias" in alias


def test_get_itbank_alias(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/alias/itbank")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, object)
    assert "alias" in data


def test_get_saved_aliases(client_auth, session):
    client, user = client_auth()

    new_alias = UserSavedAlias(alias="Test Alias", user_id=user.id)
    session.add(new_alias)
    session.commit()
    session.refresh(new_alias)

    response = client.get("/api/homebanking/alias/save")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for alias in data:
        assert "id" in alias
        assert "alias" in alias


def test_get_saved_aliases_no_aliases(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/alias/save")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "No saved aliases found"


def test_post_save_alias(client_auth, session, fake):
    client, _ = client_auth()
    other_client, other_user = client_auth()

    response = other_client.post(
        "/api/auth/register",
        json={"username": fake.user_name(), "password": "password123"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user" in data
    assert "bank_account" in data

    other_user_account = session.exec(
        select(BankAccount).where(BankAccount.user_id == other_user.id)
    ).first()

    response = client.post(f"/api/homebanking/alias/save/{other_user_account.alias}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["alias"] == other_user_account.alias


def test_post_save_alias_other_user_account_not_found(client_auth):
    client, _ = client_auth()
    response = client.post("/api/homebanking/alias/save/nonexistent-alias")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account with alias not found"


def test_post_save_alias_already_saved(client_auth, session, fake):
    client, _ = client_auth()
    other_client, other_user = client_auth()

    response = other_client.post(
        "/api/auth/register",
        json={"username": fake.user_name(), "password": "password123"},
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "user" in data
    assert "bank_account" in data

    other_user_account = session.exec(
        select(BankAccount).where(BankAccount.user_id == other_user.id)
    ).first()

    new_alias = UserSavedAlias(alias=other_user_account.alias, user_id=1)
    session.add(new_alias)
    session.commit()
    session.refresh(new_alias)

    response = client.post(f"/api/homebanking/alias/save/{other_user_account.alias}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Alias already saved"
