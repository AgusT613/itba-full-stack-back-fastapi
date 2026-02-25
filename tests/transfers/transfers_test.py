from src.constants.constants import ITBANK_TRANSFERS_COMPLETE_ENDPOINT
from src.models.accounts import BankAccount
from src.models.transfers import TransferCreate
from tests.utils import _create_user
from fastapi import status


def test_transfer_history_no_transfers(client_auth):
    """Test retrieving transfer history when there are no transfers"""
    auth_client, _ = client_auth()

    response = auth_client.get(ITBANK_TRANSFERS_COMPLETE_ENDPOINT)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []


def test_transfer_history_with_transfers(client_auth, session, fake):
    """Test retrieving transfer history when there are transfers"""
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
    assert response.status_code == status.HTTP_200_OK
    assert data["balance"] == 300.0
    assert data["sender"]["balance"] == 700.0
    assert data["receiver"]["balance"] == 800.0

    response = auth_client.get(ITBANK_TRANSFERS_COMPLETE_ENDPOINT)
    response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["balance"] == 300.0
    assert data[0]["sender_id"] == sender.id
    assert data[0]["receiver_id"] == receiver.id


def test_transfer_insufficient_funds(client_auth, session, fake):
    """Test transfer fails when sender has insufficient funds"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=100.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=500.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer_data = TransferCreate(
        account_number=receiver_account.account_number,
        balance=200.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Insufficient funds" in data["detail"]


def test_transfer_receiver_account_not_found(client_auth, session, fake):
    """Test transfer fails when receiver account doesn't exist"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.commit()
    session.refresh(sender_account)

    transfer_data = TransferCreate(
        account_number="9999999999999999",
        balance=100.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "Receiver account not found" in data["detail"]


def test_transfer_no_sender_account(client_auth, session, fake):
    """Test transfer fails when sender has no account"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=500.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(receiver_account)
    session.commit()
    session.refresh(receiver_account)

    transfer_data = TransferCreate(
        account_number=receiver_account.account_number,
        balance=100.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "Sender account not found" in data["detail"]


def test_transfer_unauthenticated(client, session, fake):
    """Test transfer fails when user is not authenticated"""
    transfer_data = TransferCreate(
        account_number="123456789",
        balance=100.0,
        receiver_id=1,
        sender_id=1,
    )

    response = client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_transfer_zero_amount(client_auth, session, fake):
    """Test transfer fails with zero amount"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=500.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer_data = TransferCreate(
        account_number=receiver_account.account_number,
        balance=0.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Transfer amount must be positive" in data["detail"]


def test_transfer_negative_amount(client_auth, session, fake):
    """Test transfer fails with negative amount"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=500.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer_data = TransferCreate(
        account_number=receiver_account.account_number,
        balance=-100.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Transfer amount must be positive" in data["detail"]


def test_transfer_to_self(client_auth, session, fake):
    """Test transfer to own account"""
    auth_client, sender = client_auth()

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.commit()
    session.refresh(sender_account)

    transfer_data = TransferCreate(
        account_number=sender_account.account_number,
        balance=100.0,
        receiver_id=sender.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert "Cannot transfer to self" in data["detail"]


def test_transfer_multiple_times(client_auth, session, fake):
    """Test multiple sequential transfers between users"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=0.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer_data_1 = TransferCreate(
        account_number=receiver_account.account_number,
        balance=100.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response1 = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data_1.model_dump(),
    )

    assert response1.status_code == status.HTTP_200_OK

    transfer_data_2 = TransferCreate(
        account_number=receiver_account.account_number,
        balance=200.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response2 = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data_2.model_dump(),
    )

    assert response2.status_code == status.HTTP_200_OK
    data = response2.json()
    assert data["sender"]["balance"] == 700.00
    assert data["receiver"]["balance"] == 300.00


def test_delete_transfer(client_auth, session, fake):
    """Test deleting a transfer"""
    auth_client, sender = client_auth()
    receiver = _create_user(session, fake)

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    receiver_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=500.00,
        user_id=receiver.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(sender_account)
    session.refresh(receiver_account)

    transfer_data = TransferCreate(
        account_number=receiver_account.account_number,
        balance=100.0,
        receiver_id=receiver.id,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    transfer_id = data["id"]

    response = auth_client.delete(f"{ITBANK_TRANSFERS_COMPLETE_ENDPOINT}/{transfer_id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Transfer deleted successfully"
    assert data["deleted_transfer"]["id"] == transfer_id
    assert data["deleted_transfer"]["balance"] == 100.0
    assert data["deleted_transfer"]["sender_id"] == sender.id
    assert data["deleted_transfer"]["receiver_id"] == receiver.id


def test_delete_transfer_receiver_account_not_found(client_auth, session, fake):
    """Test deleting a transfer when receiver account is not found"""
    auth_client, sender = client_auth()

    sender_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=sender.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(sender_account)
    session.commit()
    session.refresh(sender_account)

    transfer_data = TransferCreate(
        account_number="9999999999999999",
        balance=100.0,
        receiver_id=9999,
        sender_id=sender.id,
    )

    response = auth_client.post(
        ITBANK_TRANSFERS_COMPLETE_ENDPOINT,
        json=transfer_data.model_dump(),
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "Receiver account not found" in data["detail"]


def test_delete_transfer_not_found(client_auth, session, fake):
    """Test deleting a transfer that doesn't exist"""
    auth_client, sender = client_auth()

    response = auth_client.delete(f"{ITBANK_TRANSFERS_COMPLETE_ENDPOINT}/9999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert "Transfer not found" in data["detail"]
