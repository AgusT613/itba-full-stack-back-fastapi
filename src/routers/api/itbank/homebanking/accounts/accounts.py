from src.constants.constants import ACCOUNTS_PREFIX
from src.db.connection import SessionDep
from typing import Annotated
from src.models.users import User
from src.models.accounts import BankAccount, BankAccountCreate
from fastapi import Depends, HTTPException, APIRouter
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


@router.get("/{account_number}")
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
