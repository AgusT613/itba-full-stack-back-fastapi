from fastapi import APIRouter, Depends, status
from src.models.deposit import DepositCreate
from src.services.transfer_service import TransferServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix="/deposit", dependencies=[Depends(get_current_user)], tags=["deposit"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_deposit(
    deposit: DepositCreate,
    transfer_service: TransferServiceDep,
    current_user: CurrentUserDep,
):
    account = transfer_service.deposit_funds(current_user.id, deposit)
    return {"message": "Deposit successful", "account": account}
