from src.constants.constants import ITBANK_ACCOUNTS_COMPLETE_ENDPOINT
from src.models.accounts import BankAccount, BankAccountCreate
from tests.utils import _create_user
from fastapi import status


def test_get_my_accounts_no_accounts(client_auth):
    """Test retrieving user's accounts when they have no accounts"""
    auth_client, _ = client_auth()

    response = auth_client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_account_details_not_found(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/by/?acc_number=nonexistent&acc_id=9999"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Account not found"


def test_get_account_not_authenticated(client):
    """Test getting account details without authentication"""
    response = client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_get_my_accounts_with_accounts(client_auth, session, fake):
    """Test retrieving user's accounts when they have accounts"""
    auth_client, user = client_auth()

    account1 = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    account2 = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=2500.50,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )

    session.add(account1)
    session.add(account2)
    session.commit()
    session.refresh(account1)
    session.refresh(account2)

    response = auth_client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(acc["account_number"] == str(account1.account_number) for acc in data)
    assert any(acc["account_number"] == str(account2.account_number) for acc in data)


def test_get_account_details_success(client_auth, session, fake):
    """Test getting specific account details"""
    auth_client, user = client_auth()

    account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=5000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    response = auth_client.get(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/by/?acc_number={account.account_number}&acc_id={account.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["account_number"] == account.account_number
    assert data["balance"] == account.balance


def test_get_my_accounts_only_returns_own_accounts(client_auth, session, fake):
    """Test that get_my_accounts only returns the authenticated user's accounts"""
    auth_client, user1 = client_auth()

    user1_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=1000.00,
        user_id=user1.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(user1_account)

    user2 = _create_user(session, fake)
    user2_account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=2000.00,
        user_id=user2.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(user2_account)

    session.commit()
    session.refresh(user1_account)
    session.refresh(user2_account)

    response = auth_client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["account_number"] == user1_account.account_number


def test_get_account_details_with_invalid_format(client_auth):
    """Test getting account with invalid account number format"""
    auth_client, _ = client_auth()

    response = auth_client.get(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/invalid-format")

    assert response.status_code in [404, 422]


def test_create_account_for_user(client_auth, fake):
    """Test creating an account for the current user"""
    client, user = client_auth()

    new_account = BankAccountCreate(
        account_number=fake.bban(),
        account_type="type",
        balance=fake.random_int(min=0, max=10000),
        description=fake.text(max_nb_chars=20),
    )

    response = client.post(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}", json=new_account.model_dump()
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["user_id"] == user.id
    assert data["account_type"] == new_account.account_type
    assert data["account_number"] == new_account.account_number
    assert data["balance"] == new_account.balance
    assert data["description"] == new_account.description


def test_partial_update_account(client_auth, session, fake):
    """Test partially updating an account"""
    auth_client, user = client_auth()

    account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=3000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    update_data = {
        "account_number": account.account_number,
        "account_type": "updated_type",
    }

    response = auth_client.patch(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}", json=update_data
    )
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["account_type"] == update_data["account_type"]
    assert data["balance"] == account.balance  # balance should not be updated
    assert (
        data["description"] == account.description
    )  # description should not be updated


def test_partial_update_account_not_found(client_auth):
    """Test partially updating a non-existent account"""
    auth_client, _ = client_auth()

    update_data = {
        "account_number": "nonexistent",
        "account_type": "updated_type",
    }

    response = auth_client.patch(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}", json=update_data
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found"


def test_full_update_account(client_auth, session, fake):
    """Test fully updating an account"""
    auth_client, user = client_auth()

    account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=3000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    update_data = {
        "account_number": account.account_number,
        "account_type": "updated_type",
        "balance": 5000.00,
        "description": "Updated description",
    }

    response = auth_client.put(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}", json=update_data)
    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert data["account_type"] == update_data["account_type"]
    assert data["balance"] == update_data["balance"]
    assert data["description"] == update_data["description"]


def test_full_update_account_not_found(client_auth):
    """Test fully updating a non-existent account"""
    auth_client, _ = client_auth()

    update_data = {
        "account_number": "nonexistent",
        "account_type": "updated_type",
        "balance": 5000.00,
        "description": "Updated description",
    }

    response = auth_client.put(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}", json=update_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found"


def test_delete_account_by_number(client_auth, session, fake):
    """Test deleting an account by account number"""
    auth_client, user = client_auth()

    account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=3000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    response = auth_client.delete(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/?acc_number={account.account_number}"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Account deleted successfully"
    assert data["account_deleted"]["account_number"] == account.account_number
    assert data["account_deleted"]["id"] == account.id
    assert data["account_deleted"]["user_id"] == user.id
    assert data["account_deleted"]["account_type"] == account.account_type
    assert data["account_deleted"]["balance"] == account.balance
    assert data["account_deleted"]["description"] == account.description


def test_delete_account_by_id(client_auth, session, fake):
    """Test deleting an account by account ID"""
    auth_client, user = client_auth()

    account = BankAccount(
        account_number=fake.unique.random_number(digits=16, fix_len=True),
        balance=3000.00,
        user_id=user.id,
        account_type=fake.random_element(elements=("checking", "savings")),
        description=fake.sentence(),
    )
    session.add(account)
    session.commit()
    session.refresh(account)

    response = auth_client.delete(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/?acc_id={account.id}"
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Account deleted successfully"
    assert data["account_deleted"]["account_number"] == account.account_number
    assert data["account_deleted"]["id"] == account.id
    assert data["account_deleted"]["user_id"] == user.id
    assert data["account_deleted"]["account_type"] == account.account_type
    assert data["account_deleted"]["balance"] == account.balance
    assert data["account_deleted"]["description"] == account.description


def test_delete_account_wrong_parameters(client_auth):
    """Test deleting an account with missing parameters"""
    auth_client, _ = client_auth()

    response = auth_client.delete(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Either account_id or account_number must be provided"


def test_delete_account_not_found(client_auth):
    """Test deleting a non-existent account"""
    auth_client, _ = client_auth()

    response = auth_client.delete(
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/?acc_number=nonexistent&acc_id=9999"
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found"
