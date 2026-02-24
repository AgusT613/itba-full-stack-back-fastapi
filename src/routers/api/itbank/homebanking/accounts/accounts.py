from src.constants.constants import ACCOUNTS_PREFIX
from src.db.connection import SessionDep
from typing import Annotated
from src.models.users import User
from src.models.accounts import (
    BankAccount,
    BankAccountCreate,
    BankAccountPartialUpdate,
    BankAccountFullUpdate,
)
from fastapi import Depends, HTTPException, APIRouter, status
from src.routers.api.auth.utils import get_current_user
from sqlmodel import select

router = APIRouter(prefix=ACCOUNTS_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_my_accounts(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    accounts = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    return accounts


@router.get("/by/")
async def get_one_account(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    acc_number: str | None = None,
    acc_id: int | None = None,
):
    account = session.exec(
        select(BankAccount).where(
            (BankAccount.account_number == acc_number) | (BankAccount.id == acc_id),
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    return account


@router.post("/")
async def create_account_for_user(
    bank_account: BankAccountCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_account = BankAccount(
        account_number=bank_account.account_number,
        account_type=bank_account.account_type,
        balance=bank_account.balance,
        description=bank_account.description,
        user_id=current_user.id,
    )

    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    return new_account


@router.patch("/")
async def update_account_partially(
    bank_account: BankAccountPartialUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(
            BankAccount.account_number == bank_account.account_number,
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    account.account_type = bank_account.account_type or account.account_type
    account.balance = bank_account.balance or account.balance
    account.description = bank_account.description or account.description

    session.add(account)
    session.commit()
    session.refresh(account)

    return account


@router.put("/")
async def update_account_fully(
    bank_account: BankAccountFullUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(
            BankAccount.account_number == bank_account.account_number,
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    account.account_type = bank_account.account_type
    account.balance = bank_account.balance
    account.description = bank_account.description

    session.add(account)
    session.commit()
    session.refresh(account)

    return account


@router.delete("/")
async def delete_account(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
    acc_number: str | None = None,
    acc_id: int | None = None,
):

    if acc_id:
        statement = select(BankAccount).where(
            BankAccount.id == acc_id,
            BankAccount.user_id == current_user.id,
        )
    elif acc_number:
        statement = select(BankAccount).where(
            BankAccount.account_number == acc_number,
            BankAccount.user_id == current_user.id,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either account_id or account_number must be provided",
        )

    account = session.exec(statement).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    session.delete(account)
    session.commit()

    return {"detail": "Account deleted successfully", "account_deleted": account}
