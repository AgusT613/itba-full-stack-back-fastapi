from fastapi import APIRouter, Depends
from src.constants.constants import ACCOUNTS_PREFIX
from src.models.accounts import (
    BankAccountCreate,
    BankAccountPartialUpdate,
    BankAccountFullUpdate,
)
from src.services.account_service import AccountServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix=ACCOUNTS_PREFIX, dependencies=[Depends(get_current_user)], tags=["accounts"]
)


@router.get("/")
async def get_my_accounts(
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
):
    return account_service.get_user_accounts(current_user.id)


@router.get("/by/")
async def get_one_account(
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
    acc_number: str | None = None,
    acc_id: int | None = None,
    acc_alias: str | None = None,
):
    return account_service.get_account_by_identifier(
        user_id=current_user.id,
        acc_number=acc_number,
        acc_id=acc_id,
        acc_alias=acc_alias,
    )


@router.post("/")
async def create_account_for_user(
    bank_account: BankAccountCreate,
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
):
    return account_service.create_account(
        user_id=current_user.id,
        username=current_user.username,
        bank_account=bank_account,
    )


@router.patch("/")
async def update_account_partially(
    bank_account: BankAccountPartialUpdate,
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
):
    return account_service.update_account_partially(
        user_id=current_user.id,
        bank_account=bank_account,
    )


@router.put("/")
async def update_account_fully(
    bank_account: BankAccountFullUpdate,
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
):
    return account_service.update_account_fully(
        user_id=current_user.id,
        bank_account=bank_account,
    )


@router.delete("/")
async def delete_account(
    account_service: AccountServiceDep,
    current_user: CurrentUserDep,
    acc_number: str | None = None,
    acc_id: int | None = None,
    acc_alias: str | None = None,
):
    deleted_account = account_service.delete_account(
        user_id=current_user.id,
        acc_number=acc_number,
        acc_id=acc_id,
        acc_alias=acc_alias,
    )
    return {"detail": "Account deleted successfully", "account_deleted": deleted_account}
