from typing import Annotated
from fastapi import APIRouter, Depends
from src.constants.constants import HOME_BANKING_PREFIX
from src.routers.api.auth.utils import get_current_user
from src.models.users import User, UserHomebankingInfo
from .accounts.accounts import router as accounts_router
from .transfers.transfers import router as transfers_router
from .cards.cards import router as cards_router
from .loans.loans import router as loans_router


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])
router.include_router(accounts_router)
router.include_router(transfers_router)
router.include_router(cards_router)
router.include_router(loans_router)


@router.get("/")
async def get_homebanking(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {
        "message": f"Welcome to ITBANK Homebanking {current_user.username.capitalize()}!"
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
