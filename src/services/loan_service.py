from typing import Annotated, Any
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import EntityNotFoundError
from src.models.loans import (
    Loan,
    LoanCreate,
    LoanPartialUpdate,
    LoanFullUpdate,
)
from src.repositories.account_repository import AccountRepository
from src.repositories.loan_repository import LoanRepository


class LoanService:
    def __init__(self, session: Session):
        self.session = session
        self.loan_repo = LoanRepository(session)
        self.account_repo = AccountRepository(session)

    def get_loans(self, user_id: int) -> list[Loan]:
        return self.loan_repo.get_user_loans(user_id)

    def get_loan_by_id(self, loan_id: int, user_id: int) -> Loan:
        loan = self.loan_repo.get_user_loan(loan_id, user_id)
        if not loan:
            raise EntityNotFoundError(f"No loan found with id {loan_id}")
        return loan

    def request_loan(self, user_id: int, loan_in: LoanCreate) -> dict[str, Any]:
        user_account = self.account_repo.get_by_id(loan_in.user_account_id)
        if not user_account or user_account.user_id != user_id:
            raise EntityNotFoundError("Account not found")

        total_to_pay = loan_in.amount * loan_in.interest_rate
        new_loan = Loan(
            user_id=user_id,
            total_repayment=total_to_pay,
            amount=loan_in.amount,
            branch_office_id=loan_in.branch_office_id,
            due_date=loan_in.due_date,
            interest_rate=loan_in.interest_rate,
            loan_type=loan_in.loan_type,
            total_installments=loan_in.total_installments,
            remaining_installments=loan_in.total_installments,
            user_account_id=loan_in.user_account_id,
            status="active",
        )

        user_account.balance += loan_in.amount

        self.loan_repo.add(new_loan)
        self.account_repo.add(user_account)
        self.session.commit()
        self.loan_repo.refresh(new_loan)
        self.account_repo.refresh(user_account)

        return {"account": user_account, "loan": new_loan}

    def update_loan_partially(
        self,
        loan_id: int,
        user_id: int,
        updated_data: LoanPartialUpdate,
    ) -> Loan:
        loan = self.get_loan_by_id(loan_id, user_id)

        for key, value in updated_data.model_dump(exclude_unset=True).items():
            setattr(loan, key, value)

        self.loan_repo.add(loan)
        self.loan_repo.commit()
        self.loan_repo.refresh(loan)
        return loan

    def update_loan_fully(
        self,
        loan_id: int,
        user_id: int,
        updated_data: LoanFullUpdate,
    ) -> Loan:
        loan = self.get_loan_by_id(loan_id, user_id)

        for key, value in updated_data.model_dump().items():
            setattr(loan, key, value)

        self.loan_repo.add(loan)
        self.loan_repo.commit()
        self.loan_repo.refresh(loan)
        return loan

    def delete_loan(self, loan_id: int, user_id: int) -> Loan:
        loan = self.get_loan_by_id(loan_id, user_id)

        user_account = self.account_repo.get_by_id(loan.user_account_id)
        if user_account and user_account.user_id == user_id:
            user_account.balance -= loan.amount
            self.account_repo.add(user_account)

        self.loan_repo.delete(loan)
        self.session.commit()
        return loan


def get_loan_service(session: SessionDep) -> LoanService:
    return LoanService(session)


LoanServiceDep = Annotated[LoanService, Depends(get_loan_service)]
