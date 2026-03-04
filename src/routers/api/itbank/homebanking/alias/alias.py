from fastapi import APIRouter, Depends, status, HTTPException
from src.db.connection import SessionDep
from src.lib.auth_utils import get_current_user
from src.models.user_saved_aliases import UserSavedAlias
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


@router.post("/save/{alias}")
async def save_alias(
    alias: str,
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    account = session.exec(
        select(BankAccount).where(BankAccount.alias == alias)
    ).first()

    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account with alias not found"
        )

    alias = session.exec(
        select(UserSavedAlias).where(UserSavedAlias.alias == alias)
    ).first()

    if alias:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Alias already saved"
        )

    new_alias = UserSavedAlias(user_id=current_user.id, alias=account.alias)
    session.add(new_alias)
    session.commit()
    session.refresh(new_alias)

    return new_alias
