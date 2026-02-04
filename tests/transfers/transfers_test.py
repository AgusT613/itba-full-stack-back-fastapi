from src.constants.constants import ITBANK_TRANSFERS_COMPLETE_ENDPOINT
from src.models.accounts import BankAccount
from src.models.transfers import TransferCreate
from tests.utils import _create_user


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
