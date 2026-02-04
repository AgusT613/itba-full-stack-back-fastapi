from src.constants.constants import (
    ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT,
    ITBANK_HOMEBANKING_COMPLETE_ENDPOINT,
    ITBANK_ACCOUNTS_COMPLETE_ENDPOINT,
    ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
)
from src.models.branch_offices import BranchOffice
from src.models.transfers import TransferCreate
from src.models.accounts import BankAccount
from tests.utils import _create_user


# BRANCH OFFICES TESTS
def test_get_branch_offices_empty(client):
    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    assert response.json() == []


def test_get_one_branch_office(client, session, fake):
    branch_office = BranchOffice(
        name=fake.company(), address=fake.address(), contact=fake.phone_number()
    )

    session.add(branch_office)
    session.commit()

    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == branch_office.id
    assert data[0]["name"] == branch_office.name
    assert data[0]["address"] == branch_office.address
    assert data[0]["contact"] == branch_office.contact


# HOMEBANKING TESTS
def test_get_homebanking_welcome_message(client_auth):
    auth_client, user = client_auth()

    response = auth_client.get(ITBANK_HOMEBANKING_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert (
        data["message"]
        == f"Welcome to ITBANK Homebanking {user.username.capitalize()}!"
    )


def test_get_my_accounts_no_accounts(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_account_details_not_found(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/999999999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Account not found"


def test_transfer_history_no_transfers(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(ITBANK_TRANSFERS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_transfer_history_with_transfers(client_auth, session, fake):
    auth_client, sender = client_auth()
    receiver = _create_user(
        session, username=fake.user_name(), password=fake.password(), fake=fake
    )

    sender_account = BankAccount(
        account_number=fake.random_number(digits=16, fix_len=True),
        balance=1000.0,
        user_id=sender.id,
        account_type=fake.mime_type(),
        description="Sender account",
    )

    receiver_account = BankAccount(
        account_number=fake.random_number(digits=16, fix_len=True),
        balance=500.0,
        user_id=receiver.id,
        account_type=fake.mime_type(),
        description="Receiver account",
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer = TransferCreate(
        account_number=receiver_account.account_number,
        balance=300.0,
        sender_id=sender.id,
        receiver_id=receiver.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer.model_dump(),
    )

    data = response.json()
    assert response.status_code == 200
    assert data["balance"] == 300.0
    assert data["sender"]["balance"] == 700.0
    assert data["receiver"]["balance"] == 800.0
