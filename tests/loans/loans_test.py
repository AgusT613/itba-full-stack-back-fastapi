from fastapi import status
from src.models.loans import Loan, LoanCreate
from src.models.accounts import BankAccount


def test_get_user_loans_empty(client_auth):
    client, _ = client_auth()

    response = client.get("/api/homebanking/loans")
    data = response.json()

    assert data == []
    assert response.status_code == status.HTTP_200_OK


def test_get_loans(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
    )

    session.add(user_account)
    session.commit()
    session.refresh(user_account)

    loan = Loan(
        amount=fake.random_int(min=0, max=100),
        branch_office_id=0,
        user_id=user.id,
        due_date=fake.date_time().timestamp(),
        interest_rate=0.15,
        loan_type="hipotecario",
        remaining_installments=24,
        start_date=fake.date_time(),
        status="active",
        total_installments=24,
        total_repayment=60000000,
        user_account_id=user_account.user_id,
    )

    session.add(loan)
    session.commit()
    session.refresh(loan)

    response = client.get("/api/homebanking/loans")
    data = response.json()

    assert len(data) == 1
    assert data[0]["user_id"] == user.id
    assert data[0]["branch_office_id"] == loan.branch_office_id
    assert data[0]["id"] == loan.id


def test_get_loan_by_id(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
    )

    session.add(user_account)
    session.commit()
    session.refresh(user_account)

    loan = Loan(
        amount=fake.random_int(min=0, max=100),
        branch_office_id=0,
        user_id=user.id,
        due_date=fake.date_time().timestamp(),
        interest_rate=0.15,
        loan_type="hipotecario",
        remaining_installments=24,
        start_date=fake.date_time(),
        status="active",
        total_installments=24,
        total_repayment=60000000,
        user_account_id=user_account.user_id,
    )

    session.add(loan)
    session.commit()
    session.refresh(loan)

    response = client.get("/api/homebanking/loans/1")
    data = response.json()

    assert data["id"] == 1
    assert data["user_id"] == user.id
    assert data["branch_office_id"] == loan.branch_office_id
    assert data["id"] == loan.id


def test_request_loan(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
    )

    session.add(user_account)
    session.commit()
    session.refresh(user_account)

    loan = LoanCreate(
        amount=1000,
        branch_office_id=0,
        due_date=fake.future_datetime().timestamp(),
        interest_rate=0.15,
        loan_type="type",
        remaining_installments=24,
        total_installments=24,
        user_account_id=user_account.id,
    )

    response = client.post("/api/homebanking/loans", json=loan.model_dump())
    data = response.json()

    assert data["account"]["id"] == 1
    assert data["account"]["user_id"] == 1
    assert data["loan"]["user_id"] == user.id
    assert data["loan"]["branch_office_id"] == loan.branch_office_id
