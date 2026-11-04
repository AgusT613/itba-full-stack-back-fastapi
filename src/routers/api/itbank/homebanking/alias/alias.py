from fastapi import APIRouter, Depends
from src.services.alias_service import AliasServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix="/alias", dependencies=[Depends(get_current_user)], tags=["alias"]
)


@router.get("/all")
async def get_aliases(current_user: CurrentUserDep, alias_service: AliasServiceDep):
    return alias_service.get_all_account_aliases(current_user.id)


@router.get("/itbank")
async def get_itbank_alias(current_user: CurrentUserDep, alias_service: AliasServiceDep):
    return alias_service.get_itbank_alias(current_user.id)


@router.get("/save")
async def get_saved_aliases(current_user: CurrentUserDep, alias_service: AliasServiceDep):
    return alias_service.get_saved_aliases(current_user.id)


@router.post("/save/{alias}")
async def save_alias(
    alias: str,
    current_user: CurrentUserDep,
    alias_service: AliasServiceDep,
):
    return alias_service.save_alias(current_user.id, alias)
