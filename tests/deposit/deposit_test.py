from sqlmodel import select
from src.models.accounts import BankAccount
from src.models.deposit import DepositCreate
from fastapi import status


def test_deposit(client_auth, session):
    client, user = client_auth()

    account = session.exec(
        select(BankAccount).where(BankAccount.user_id == user.id)
    ).first()

    deposit = DepositCreate(alias=account.alias, amount=1000)
    response = client.post("/api/homebanking/deposit", json=deposit.model_dump())

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["message"] == "Deposit successful"
    assert data["account"]["balance"] == 1000


def test_deposit_account_not_found(client_auth):
    client, _ = client_auth()

    deposit = DepositCreate(alias="nonexistent", amount=1000)
    response = client.post("/api/homebanking/deposit", json=deposit.model_dump())

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found"
