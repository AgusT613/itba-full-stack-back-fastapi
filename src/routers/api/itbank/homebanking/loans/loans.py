from sqlmodel import select
from fastapi import APIRouter, Depends, HTTPException, status
from src.routers.api.auth.utils import get_current_user
from src.db.connection import SessionDep
from typing import Annotated
from src.models.users import User
from src.models.accounts import BankAccount
from src.models.loans import Loan, LoanCreate

router = APIRouter(prefix="/loans", dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_loan_list(
    session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]
):
    loans = session.exec(select(Loan).where(Loan.user_id == current_user.id)).all()

    return loans


@router.get("/{loan_id}")
async def get_loan_by_id(
    loan_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    loan = session.exec(
        select(Loan).where(Loan.id == loan_id, Loan.user_id == current_user.id)
    ).first()

    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No loan found with id {loan_id}",
        )

    return loan


@router.post("/")
async def request_loan(
    loan: LoanCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_account = session.exec(
        select(BankAccount).where(
            BankAccount.id == loan.user_account_id,
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not user_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
        )

    total_to_pay = loan.amount * loan.interest_rate
    new_loan = Loan(
        user_id=current_user.id,
        total_repayment=total_to_pay,
        amount=loan.amount,
        branch_office_id=loan.branch_office_id,
        due_date=loan.due_date,
        interest_rate=loan.interest_rate,
        loan_type=loan.loan_type,
        total_installments=loan.total_installments,
        remaining_installments=loan.remaining_installments,
        user_account_id=loan.user_account_id,
        status="active",
    )

    user_account.balance += loan.amount

    session.add(new_loan)
    session.add(user_account)
    session.commit()
    session.refresh(new_loan)
    session.refresh(user_account)

    return {"account": user_account, "loan": new_loan}
