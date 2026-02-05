from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.constants.constants import (
    HOME_BANKING_PREFIX,
    ACCOUNTS_PREFIX,
    TRANSFERS_PREFIX,
)
from src.routers.api.auth.utils import get_current_user
from src.models.users import User
from src.db.connection import SessionDep
from src.models.accounts import BankAccount
from src.models.transfers import Transfer, TransferCreate
from sqlmodel import select


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_homebanking(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {
        "message": f"Welcome to ITBANK Homebanking {current_user.username.capitalize()}!"
    }


# ACCOUNTS
@router.get(ACCOUNTS_PREFIX)
async def get_my_accounts(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    accounts = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    return accounts


@router.get(f"{ACCOUNTS_PREFIX}/{{account_number}}")
async def get_account_details(
    account_number: str,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(
            BankAccount.account_number == account_number,
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


# TRANSFERS
@router.get(f"{TRANSFERS_PREFIX}")
async def get_transfer_history(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    transfers = session.exec(
        select(Transfer).where(
            Transfer.sender_id == current_user.id,
            Transfer.receiver_id == current_user.id,
        )
    ).all()

    return transfers


@router.post(f"{TRANSFERS_PREFIX}")
async def make_transfer(
    transfer: TransferCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    sender_account = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).first()

    receiver_account = session.exec(
        select(BankAccount).where(
            BankAccount.user_id == transfer.receiver_id
            and BankAccount.account_number == transfer.account_number
        )
    ).first()

    if not receiver_account:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    if sender_account.balance < transfer.balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    sender_account.balance -= transfer.balance
    receiver_account.balance += transfer.balance

    transfer = Transfer(
        sender_id=current_user.id,
        receiver_id=receiver_account.user_id,
        balance=transfer.balance,
    )

    session.add(transfer)
    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(transfer)
    session.refresh(sender_account)
    session.refresh(receiver_account)

    return {
        "sender": sender_account,
        "receiver": receiver_account,
        "balance": transfer.balance,
    }
