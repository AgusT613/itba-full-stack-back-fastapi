from fastapi import APIRouter, Depends
from src.constants.constants import TRANSFERS_PREFIX
from src.models.transfers import TransferCreate
from src.services.transfer_service import TransferServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix=TRANSFERS_PREFIX,
    dependencies=[Depends(get_current_user)],
    tags=["transfers"],
)


@router.get("/")
async def get_transfer_history(
    transfer_service: TransferServiceDep,
    current_user: CurrentUserDep,
):
    return transfer_service.get_transfer_history(current_user.id)


@router.post("/")
async def make_transfer(
    transfer: TransferCreate,
    transfer_service: TransferServiceDep,
    current_user: CurrentUserDep,
):
    return transfer_service.make_transfer(current_user.id, transfer)


@router.delete("/{transfer_id}")
async def delete_transfer(
    transfer_id: int,
    transfer_service: TransferServiceDep,
    current_user: CurrentUserDep,
):
    deleted_transfer = transfer_service.delete_transfer(transfer_id, current_user.id)
    return {"detail": "Transfer deleted successfully", "deleted_transfer": deleted_transfer}
