from sqlmodel import select
from typing import Annotated
from fastapi import APIRouter, Depends
from src.constants.constants import HOME_BANKING_PREFIX
from src.db.connection import SessionDep
from src.models.accounts import BankAccount
from src.models.cards import Card, CardResponseModel
from src.models.transfers import Transfer, TransferResponseModel
from src.lib.auth_utils import get_current_user
from src.models.users import User, UserHomebankingInfo, UserResponseModel
from .accounts.accounts import router as accounts_router
from .transfers.transfers import router as transfers_router
from .cards.cards import router as cards_router
from .loans.loans import router as loans_router
from .alias.alias import router as alias_router
from .deposit.deposit import router as deposit_router


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])
router.include_router(accounts_router)
router.include_router(transfers_router)
router.include_router(cards_router)
router.include_router(loans_router)
router.include_router(alias_router)
router.include_router(deposit_router)


@router.get("/")
async def get_homebanking(
    current_user: Annotated[User, Depends(get_current_user)],
    session: SessionDep,
):
    bank_account = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).first()

    cards = session.exec(select(Card).where(Card.user_id == current_user.id)).all()
    cards_response = [
        CardResponseModel(
            account_id=card.account_id,
            card_type=card.card_type,
            last_four=card.last_four,
            card_holder_name=card.card_holder_name,
            expiration_date=card.expiration_date,
            brand=card.brand,
            status=card.status,
            id=card.id,
        )
        for card in cards
    ]

    transfers = session.exec(
        select(Transfer, User)
        .join(User, onclause=Transfer.receiver_id == User.id)
        .where(Transfer.sender_id == current_user.id)
    ).all()
    transfers_response = [
        TransferResponseModel(
            id=transfer.id,
            receiver_username=user.username,
            balance=transfer.balance,
            transfer_date=transfer.transfer_date,
        )
        for transfer, user in transfers
    ]

    return {
        "user": UserHomebankingInfo(
            email=current_user.email,
            full_name=current_user.full_name,
            username=current_user.username,
        ),
        "itbank_account": bank_account,
        "cards": cards_response,
        "transfers": transfers_response,
    }


@router.get("/me")
async def get_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    user = UserHomebankingInfo(
        email=current_user.email,
        full_name=current_user.full_name,
        username=current_user.username,
    )

    return user


@router.get("/users")
async def get_all_users(
    session: SessionDep,
):
    users = session.exec(select(User)).all()

    users_response = [
        UserResponseModel(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            username=user.username,
        )
        for user in users
    ]

    return users_response
