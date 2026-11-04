from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import EntityNotFoundError, InvalidOperationError
from src.models.accounts import (
    BankAccount,
    BankAccountCreate,
    BankAccountPartialUpdate,
    BankAccountFullUpdate,
)
from src.repositories.account_repository import AccountRepository
from src.utils.text_generation import get_bank_alias


class AccountService:
    def __init__(self, session: Session):
        self.session = session
        self.repo = AccountRepository(session)

    def get_user_accounts(self, user_id: int) -> list[BankAccount]:
        return self.repo.get_user_accounts(user_id)

    def get_account_by_identifier(
        self,
        user_id: int,
        acc_number: str | None = None,
        acc_id: int | None = None,
        acc_alias: str | None = None,
    ) -> BankAccount:
        if not acc_number and not acc_id and not acc_alias:
            raise InvalidOperationError(
                "Either account_id, account_number or account_alias must be provided"
            )

        account = self.repo.get_user_account_by_identifier(
            user_id=user_id,
            acc_number=acc_number,
            acc_id=acc_id,
            acc_alias=acc_alias,
        )
        if not account:
            raise EntityNotFoundError("Account not found")
        return account

    def create_account(
        self,
        user_id: int,
        username: str,
        bank_account: BankAccountCreate,
    ) -> BankAccount:
        new_account = BankAccount(
            account_number=bank_account.account_number,
            account_type=bank_account.account_type,
            balance=bank_account.balance,
            description=bank_account.description,
            alias=get_bank_alias(username),
            user_id=user_id,
        )
        self.repo.add(new_account)
        self.repo.commit()
        self.repo.refresh(new_account)
        return new_account

    def update_account_partially(
        self,
        user_id: int,
        bank_account: BankAccountPartialUpdate,
    ) -> BankAccount:
        account = self.repo.get_user_account_by_identifier(
            user_id=user_id,
            acc_number=bank_account.account_number,
        )
        if not account:
            raise EntityNotFoundError("Account not found")

        if bank_account.account_type is not None:
            account.account_type = bank_account.account_type
        if bank_account.balance is not None:
            account.balance = bank_account.balance
        if bank_account.description is not None:
            account.description = bank_account.description
        if bank_account.alias is not None:
            account.alias = bank_account.alias

        self.repo.add(account)
        self.repo.commit()
        self.repo.refresh(account)
        return account

    def update_account_fully(
        self,
        user_id: int,
        bank_account: BankAccountFullUpdate,
    ) -> BankAccount:
        account = self.repo.get_user_account_by_identifier(
            user_id=user_id,
            acc_number=bank_account.account_number,
        )
        if not account:
            raise EntityNotFoundError("Account not found")

        account.account_type = bank_account.account_type
        account.balance = bank_account.balance
        account.description = bank_account.description
        account.alias = bank_account.alias

        self.repo.add(account)
        self.repo.commit()
        self.repo.refresh(account)
        return account

    def delete_account(
        self,
        user_id: int,
        acc_number: str | None = None,
        acc_id: int | None = None,
        acc_alias: str | None = None,
    ) -> BankAccount:
        account = self.get_account_by_identifier(
            user_id=user_id,
            acc_number=acc_number,
            acc_id=acc_id,
            acc_alias=acc_alias,
        )
        self.repo.delete(account)
        self.repo.commit()
        return account


def get_account_service(session: SessionDep) -> AccountService:
    return AccountService(session)


AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]
