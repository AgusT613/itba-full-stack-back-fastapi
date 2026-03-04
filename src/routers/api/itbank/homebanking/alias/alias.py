from fastapi import APIRouter, Depends, status, HTTPException
from src.db.connection import SessionDep
from src.lib.auth_utils import get_current_user
from src.models.users import User
from typing import Annotated
from src.models.accounts import BankAccount
from sqlmodel import select

router = APIRouter(prefix="/alias", dependencies=[Depends(get_current_user)])


@router.get("/all")
async def get_aliases(
    current_user: Annotated[User, Depends(get_current_user)], session: SessionDep
):
    accounts = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    if not accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No accounts found"
        )

    aliases = [{"alias": account.alias} for account in accounts]

    return aliases


@router.get("/itbank")
async def get_itbank_alias(
    current_user: Annotated[User, Depends(get_current_user)], session: SessionDep
):
    account = session.exec(
        select(BankAccount).where(
            BankAccount.user_id == current_user.id, BankAccount.account_type == "itbank"
        )
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="ITBANK account not found"
        )

    return {"alias": account.alias}
