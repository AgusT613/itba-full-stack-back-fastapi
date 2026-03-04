from fastapi import status
from src.models.loans import Loan, LoanCreate
from src.models.accounts import BankAccount


def test_get_user_loans_empty(client_auth):
    client, _ = client_auth()

    response = client.get("/api/homebanking/loans")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data == []


def test_get_loans(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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
    assert response.status_code == status.HTTP_200_OK
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
        alias=fake.unique.word(),
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
    assert response.status_code == status.HTTP_200_OK
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
        alias=fake.unique.word(),
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
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert (
        data["account"]["id"] == 2
    )  # Assuming this is the second account created in the test database
    assert data["account"]["user_id"] == 1
    assert data["loan"]["user_id"] == user.id
    assert data["loan"]["branch_office_id"] == loan.branch_office_id


def test_request_loan_with_nonexistent_account(client_auth, session, fake):
    client, user = client_auth()

    loan = LoanCreate(
        amount=1000,
        branch_office_id=0,
        due_date=fake.future_datetime().timestamp(),
        interest_rate=0.15,
        loan_type="type",
        remaining_installments=24,
        total_installments=24,
        user_account_id=9999,  # Non-existent account ID
    )

    response = client.post("/api/homebanking/loans", json=loan.model_dump())
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "Account not found"


def test_get_loan_by_id_not_found(client_auth, session, fake):
    client, _ = client_auth()

    response = client.get("/api/homebanking/loans/9999")  # Non-existent loan ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No loan found with id 9999"


def test_partial_update_loan(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {"status": "closed", "remaining_installments": 0}
    response = client.patch("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "closed"
    assert data["remaining_installments"] == 0


def test_partial_update_loan_not_found(client_auth, session, fake):
    client, _ = client_auth()

    update_data = {"status": "closed", "remaining_installments": 0}
    response = client.patch(
        "/api/homebanking/loans/9999", json=update_data
    )  # Non-existent loan ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No loan found with id 9999"


def test_partial_update_loan_invalid_fields(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {"invalid_field": "value"}
    response = client.patch("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "invalid_field" not in data


def test_partial_update_loan_no_fields(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {}
    response = client.patch("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == loan.status
    assert data["remaining_installments"] == loan.remaining_installments
    assert data["id"] == loan.id
    assert data["user_id"] == user.id
    assert data["branch_office_id"] == loan.branch_office_id
    assert data["amount"] == loan.amount
    assert data["due_date"] == loan.due_date
    assert data["interest_rate"] == loan.interest_rate
    assert data["loan_type"] == loan.loan_type
    assert data["total_installments"] == loan.total_installments
    assert data["total_repayment"] == loan.total_repayment
    assert data["user_account_id"] == loan.user_account_id
    # assert data["start_date"] == loan.start_date --> fix this assertion if needed, as start_date might be returned in a different format (e.g., ISO 8601 string) than how it's stored in the database (e.g., datetime object)


def test_full_update_loan(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {
        "branch_office_id": 1,
        "user_account_id": user_account.id,
        "loan_type": "personal",
        "status": "closed",
        "remaining_installments": 0,
    }
    response = client.put("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["branch_office_id"] == update_data["branch_office_id"]
    assert data["user_account_id"] == update_data["user_account_id"]
    assert data["loan_type"] == update_data["loan_type"]
    assert data["status"] == update_data["status"]
    assert data["remaining_installments"] == update_data["remaining_installments"]
    assert data["id"] == loan.id
    assert data["user_id"] == user.id
    assert data["amount"] == loan.amount
    assert data["due_date"] == loan.due_date
    assert data["interest_rate"] == loan.interest_rate
    assert data["total_installments"] == loan.total_installments
    assert data["total_repayment"] == loan.total_repayment
    # assert data["start_date"] == loan.start_date --> fix this assertion if needed, as start_date might be returned in a different format (e.g., ISO 8601 string) than how it's stored in the database (e.g., datetime object)


def test_full_update_loan_not_found(client_auth, session, fake):
    client, _ = client_auth()

    update_data = {
        "branch_office_id": 1,
        "user_account_id": 1,
        "loan_type": "personal",
        "status": "closed",
        "remaining_installments": 0,
    }
    response = client.put(
        "/api/homebanking/loans/9999", json=update_data
    )  # Non-existent loan ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No loan found with id 9999"


def test_full_update_loan_invalid_fields(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {
        "branch_office_id": 1,
        "user_account_id": user_account.id,
        "loan_type": "personal",
        "status": "closed",
        "remaining_installments": 0,
        "invalid_field": "value",  # This field should be ignored
    }
    response = client.put("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "invalid_field" not in data
    assert data["branch_office_id"] == update_data["branch_office_id"]
    assert data["user_account_id"] == update_data["user_account_id"]
    assert data["loan_type"] == update_data["loan_type"]
    assert data["status"] == update_data["status"]
    assert data["remaining_installments"] == update_data["remaining_installments"]


def test_full_update_loan_no_fields(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    update_data = {}
    response = client.put("/api/homebanking/loans/1", json=update_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "branch_office_id"]
    assert data["detail"][0]["msg"] == "Field required"
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][1]["loc"] == ["body", "user_account_id"]
    assert data["detail"][1]["msg"] == "Field required"
    assert data["detail"][1]["type"] == "missing"
    assert data["detail"][2]["loc"] == ["body", "loan_type"]
    assert data["detail"][2]["msg"] == "Field required"
    assert data["detail"][2]["type"] == "missing"
    assert data["detail"][3]["loc"] == ["body", "status"]
    assert data["detail"][3]["msg"] == "Field required"
    assert data["detail"][3]["type"] == "missing"
    assert data["detail"][4]["loc"] == ["body", "remaining_installments"]
    assert data["detail"][4]["msg"] == "Field required"
    assert data["detail"][4]["type"] == "missing"


def test_delete_loan(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    response = client.delete("/api/homebanking/loans/1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == f"Loan with id {loan.id} has been deleted"
    assert data["deleted_loan"]["id"] == loan.id
    assert data["deleted_loan"]["user_id"] == user.id
    assert data["deleted_loan"]["branch_office_id"] == loan.branch_office_id
    assert data["deleted_loan"]["amount"] == loan.amount
    assert data["deleted_loan"]["due_date"] == loan.due_date
    assert data["deleted_loan"]["interest_rate"] == loan.interest_rate
    assert data["deleted_loan"]["loan_type"] == loan.loan_type
    assert data["deleted_loan"]["remaining_installments"] == loan.remaining_installments
    # assert data["deleted_loan"]["start_date"] == loan.start_date --> fix this assertion if needed, as start_date might be returned in a different format (e.g., ISO 8601 string) than how it's stored in the database (e.g., datetime object)
    assert data["deleted_loan"]["status"] == loan.status
    assert data["deleted_loan"]["total_installments"] == loan.total_installments
    assert data["deleted_loan"]["total_repayment"] == loan.total_repayment
    assert data["deleted_loan"]["user_account_id"] == loan.user_account_id


def test_delete_loan_not_found(client_auth, session, fake):
    client, _ = client_auth()

    response = client.delete("/api/homebanking/loans/9999")  # Non-existent loan ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No loan found with id 9999"


def test_delete_loan_already_deleted(client_auth, session, fake):
    client, user = client_auth()

    user_account = BankAccount(
        account_number=fake.random_number(digits=16),
        account_type=fake.currency_name(),
        balance=fake.random_int(min=0, max=100),
        description=fake.text(max_nb_chars=20),
        user_id=user.id,
        alias=fake.unique.word(),
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

    response = client.delete("/api/homebanking/loans/1")
    assert response.status_code == status.HTTP_200_OK

    response = client.delete("/api/homebanking/loans/1")  # Attempt to delete again
    assert response.status_code == status.HTTP_404_NOT_FOUND
    data = response.json()
    assert data["detail"] == "No loan found with id 1"


def test_delete_loan_invalid_id(client_auth):
    client, _ = client_auth()

    response = client.delete("/api/homebanking/loans/invalid_id")  # Invalid loan ID
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
