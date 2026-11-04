from fastapi import APIRouter, Depends
from src.constants.constants import HOME_BANKING_PREFIX
from src.models.users import UserHomebankingInfo, UserResponseModel
from src.services.homebanking_service import HomebankingServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user
from .accounts.accounts import router as accounts_router
from .alias.alias import router as alias_router
from .cards.cards import router as cards_router
from .deposit.deposit import router as deposit_router
from .loans.loans import router as loans_router
from .transfers.transfers import router as transfers_router

router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])
router.include_router(accounts_router)
router.include_router(transfers_router)
router.include_router(cards_router)
router.include_router(loans_router)
router.include_router(alias_router)
router.include_router(deposit_router)


@router.get("/")
async def get_homebanking(
    current_user: CurrentUserDep,
    homebanking_service: HomebankingServiceDep,
):
    return homebanking_service.get_dashboard(current_user)


@router.get("/me")
async def get_current_user_profile(
    current_user: CurrentUserDep,
):
    return UserHomebankingInfo(
        email=current_user.email,
        full_name=current_user.full_name,
        username=current_user.username,
    )


@router.get("/users", response_model=list[UserResponseModel])
async def get_all_users(
    homebanking_service: HomebankingServiceDep,
):
    return homebanking_service.get_all_users()
