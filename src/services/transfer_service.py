from typing import Annotated, Any
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import (
    EntityNotFoundError,
    InsufficientFundsError,
    InvalidOperationError,
)
from src.models.accounts import BankAccount
from src.models.deposit import DepositCreate
from src.models.transfers import Transfer, TransferCreate, TransferResponseModel
from src.repositories.account_repository import AccountRepository
from src.repositories.transfer_repository import TransferRepository


class TransferService:
    def __init__(self, session: Session):
        self.session = session
        self.transfer_repo = TransferRepository(session)
        self.account_repo = AccountRepository(session)

    def get_transfer_history(self, user_id: int) -> list[TransferResponseModel]:
        results = self.transfer_repo.get_user_transfer_history(user_id)
        return [
            TransferResponseModel(
                id=transfer.id,
                sender_username=sender.username,
                receiver_username=receiver.username,
                balance=transfer.balance,
                transfer_date=transfer.transfer_date,
                transfer_type=transfer.transfer_type,
            )
            for transfer, sender, receiver in results
        ]

    def make_transfer(
        self,
        user_id: int,
        transfer: TransferCreate,
    ) -> dict[str, Any]:
        sender_account = self.account_repo.get_user_account_by_alias(
            user_id=user_id,
            alias=transfer.sender_alias,
        )
        if not sender_account:
            raise EntityNotFoundError("Sender account not found")

        receiver_account = self.account_repo.get_by_alias(transfer.receiver_alias)
        if not receiver_account:
            raise EntityNotFoundError("Receiver account not found")

        if sender_account.balance < transfer.balance:
            raise InsufficientFundsError("Insufficient funds")

        if transfer.balance <= 0:
            raise InvalidOperationError("Transfer amount must be positive")

        if sender_account.alias == receiver_account.alias:
            raise InvalidOperationError("Cannot transfer to self")

        sender_account.balance -= transfer.balance
        receiver_account.balance += transfer.balance

        new_transfer = Transfer(
            sender_id=user_id,
            receiver_id=receiver_account.user_id,
            balance=transfer.balance,
        )

        self.transfer_repo.add(new_transfer)
        self.account_repo.add(sender_account)
        self.account_repo.add(receiver_account)
        self.session.commit()

        self.transfer_repo.refresh(new_transfer)
        self.account_repo.refresh(sender_account)
        self.account_repo.refresh(receiver_account)

        return {
            "id": new_transfer.id,
            "sender": sender_account,
            "receiver": receiver_account,
            "balance": new_transfer.balance,
            "transfer_date": new_transfer.transfer_date,
            "transfer_type": new_transfer.transfer_type,
        }

    def delete_transfer(self, transfer_id: int, user_id: int) -> Transfer:
        transfer = self.transfer_repo.get_user_transfer(transfer_id, user_id)
        if not transfer:
            raise EntityNotFoundError("Transfer not found")

        self.transfer_repo.delete(transfer)
        self.transfer_repo.commit()
        return transfer

    def deposit_funds(self, user_id: int, deposit: DepositCreate) -> BankAccount:
        account = self.account_repo.get_user_account_by_alias(user_id, deposit.alias)
        if not account:
            raise EntityNotFoundError("Account not found")

        account.balance += deposit.amount

        transfer = Transfer(
            balance=deposit.amount,
            sender_id=user_id,
            receiver_id=user_id,
            transfer_type="deposit",
        )

        self.account_repo.add(account)
        self.transfer_repo.add(transfer)
        self.session.commit()
        self.account_repo.refresh(account)
        self.transfer_repo.refresh(transfer)

        return account


def get_transfer_service(session: SessionDep) -> TransferService:
    return TransferService(session)


TransferServiceDep = Annotated[TransferService, Depends(get_transfer_service)]
