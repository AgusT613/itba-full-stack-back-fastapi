from sqlmodel import select
from src.models.transfers import Transfer, TransferCreate, TransferResponseModel
from fastapi import APIRouter, Depends, HTTPException
from src.constants.constants import TRANSFERS_PREFIX
from src.lib.auth_utils import get_current_user
from src.db.connection import SessionDep
from typing import Annotated
from src.models.users import User
from src.models.accounts import BankAccount

router = APIRouter(prefix=TRANSFERS_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_transfer_history(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    results = session.exec(
        select(Transfer, User)
        .join(
            User,
            onclause=(Transfer.receiver_id == User.id | Transfer.sender_id == User.id),
        )
        .where(
            (Transfer.sender_id == current_user.id)
            | (Transfer.receiver_id == current_user.id)
        )
    ).all()

    response = [
        TransferResponseModel(
            id=transfer.id,
            sender_username=current_user.username,
            receiver_username=user.username,
            balance=transfer.balance,
            transfer_date=transfer.transfer_date,
            transfer_type=transfer.transfer_type,
        )
        for transfer, user in results
    ]

    return response


@router.post("/")
async def make_transfer(
    transfer: TransferCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    sender_account = session.exec(
        select(BankAccount).where(
            BankAccount.user_id == current_user.id,
            BankAccount.alias == transfer.sender_alias,
        )
    ).first()

    receiver_account = session.exec(
        select(BankAccount).where(BankAccount.alias == transfer.receiver_alias)
    ).first()

    if not sender_account:
        raise HTTPException(status_code=404, detail="Sender account not found")

    if not receiver_account:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    if sender_account.balance < transfer.balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    if transfer.balance <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    if sender_account.alias == receiver_account.alias:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")

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
        "id": transfer.id,
        "sender": sender_account,
        "receiver": receiver_account,
        "balance": transfer.balance,
        "transfer_date": transfer.transfer_date,
        "transfer_type": transfer.transfer_type,
    }


@router.delete("/{transfer_id}")
async def delete_transfer(
    transfer_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    transfer = session.exec(
        select(Transfer).where(
            Transfer.id == transfer_id,
            Transfer.sender_id == current_user.id,
        )
    ).first()

    if not transfer:
        raise HTTPException(status_code=404, detail="Transfer not found")

    session.delete(transfer)
    session.commit()

    return {"detail": "Transfer deleted successfully", "deleted_transfer": transfer}
