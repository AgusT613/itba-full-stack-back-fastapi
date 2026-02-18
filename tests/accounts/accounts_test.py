from src.constants.constants import ITBANK_ACCOUNTS_COMPLETE_ENDPOINT
from src.models.accounts import BankAccount
from tests.utils import _create_user


def test_get_my_accounts_no_accounts(client_auth):
    """Test retrieving user's accounts when they have no accounts"""
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
        f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/{account.account_number}"
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
