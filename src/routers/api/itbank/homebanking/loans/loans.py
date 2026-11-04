from fastapi import APIRouter, Depends, status
from src.models.loans import LoanCreate, LoanFullUpdate, LoanPartialUpdate
from src.services.loan_service import LoanServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix="/loans", dependencies=[Depends(get_current_user)], tags=["loans"]
)


@router.get("/")
async def get_loan_list(loan_service: LoanServiceDep, current_user: CurrentUserDep):
    return loan_service.get_loans(current_user.id)


@router.get("/{loan_id}")
async def get_loan_by_id(
    loan_id: int,
    loan_service: LoanServiceDep,
    current_user: CurrentUserDep,
):
    return loan_service.get_loan_by_id(loan_id, current_user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def request_loan(
    loan: LoanCreate,
    loan_service: LoanServiceDep,
    current_user: CurrentUserDep,
):
    return loan_service.request_loan(current_user.id, loan)


@router.patch("/{loan_id}")
async def partial_update_loan(
    loan_id: int,
    updated_loan_data: LoanPartialUpdate,
    loan_service: LoanServiceDep,
    current_user: CurrentUserDep,
):
    return loan_service.update_loan_partially(loan_id, current_user.id, updated_loan_data)


@router.put("/{loan_id}")
async def full_update_loan(
    loan_id: int,
    updated_loan_data: LoanFullUpdate,
    loan_service: LoanServiceDep,
    current_user: CurrentUserDep,
):
    return loan_service.update_loan_fully(loan_id, current_user.id, updated_loan_data)


@router.delete("/{loan_id}")
async def delete_loan(
    loan_id: int,
    loan_service: LoanServiceDep,
    current_user: CurrentUserDep,
):
    deleted_loan = loan_service.delete_loan(loan_id, current_user.id)
    return {"detail": f"Loan with id {loan_id} has been deleted", "deleted_loan": deleted_loan}
