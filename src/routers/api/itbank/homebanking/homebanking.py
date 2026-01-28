from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from src.constants.constants import HOME_BANKING_PREFIX
from src.routers.api.auth.utils import get_current_user
from src.models.users import User
from src.db.connection import SessionDep
from src.models.accounts import BankAccount
from sqlmodel import select


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_homebanking(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {"message": f"Welcome to ITBANK Homebanking {current_user.username.capitalize()}!"}


@router.get("/accounts")
async def get_my_accounts(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    accounts = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    return accounts


@router.get("/accounts/{account_number}")
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

    if account.owner_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="You do not have permission to view this account"
        )

    return account
