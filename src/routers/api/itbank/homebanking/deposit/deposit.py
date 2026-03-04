from fastapi import APIRouter, Depends, status, HTTPException
from sqlmodel import select
from src.db.connection import SessionDep
from src.lib.auth_utils import get_current_user
from src.models.accounts import BankAccount
from src.models.transfers import Transfer
from src.models.users import User
from typing import Annotated
from src.models.deposit import DepositCreate

router = APIRouter(prefix="/deposit", dependencies=[Depends(get_current_user)])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit: DepositCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(
            User.id == current_user.id, BankAccount.alias == deposit.alias
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    account.balance += deposit.amount

    transfer = Transfer(
        balance=deposit.amount,
        sender_id=account.id,
        receiver_id=account.id,
        transfer_type="deposit",
    )

    session.add(account)
    session.add(transfer)
    session.commit()
    session.refresh(account)
    session.refresh(transfer)

    return {"message": "Deposit successful", "account": account}
