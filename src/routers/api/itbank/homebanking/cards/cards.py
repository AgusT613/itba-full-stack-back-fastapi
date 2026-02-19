from fastapi import APIRouter, Depends
from src.routers.api.auth.utils import get_current_user
from src.db.connection import SessionDep
from sqlmodel import select
from src.models.cards import Card
from src.models.accounts import BankAccount
from src.models.users import User
from typing import Annotated

router = APIRouter(prefix="/cards", dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_card_list(
    session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]
):
    cards = session.exec(
        select(Card).where(
            Card.account_id == BankAccount.id, User.id == current_user.id
        )
    ).all()

    return cards
