from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from src.constants.constants import (
    HOME_BANKING_PREFIX,
    ACCOUNTS_PREFIX,
    TRANSFERS_PREFIX,
)
from src.routers.api.auth.utils import get_current_user
from src.models.users import User
from src.db.connection import SessionDep
from src.models.accounts import BankAccount, BankAccountCreate
from src.models.cards import Card
from src.models.transfers import Transfer, TransferCreate
from src.models.loans import Loan, LoanCreate
from sqlmodel import select


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_homebanking(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {
        "message": f"Welcome to ITBANK Homebanking {current_user.username.capitalize()}!"
    }


# ACCOUNTS
@router.get(ACCOUNTS_PREFIX)
async def get_my_accounts(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    accounts = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).all()

    return accounts


@router.get(f"{ACCOUNTS_PREFIX}/{{account_number}}")
async def get_account_details(
    account_number: str,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(
            BankAccount.account_number == account_number,
            BankAccount.user_id == current_user.id,
        )
    ).first()

    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return account


@router.post(ACCOUNTS_PREFIX)
async def create_account_for_user(
    bank_account: BankAccountCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    new_account = BankAccount(
        account_number=bank_account.account_number,
        account_type=bank_account.account_type,
        balance=bank_account.balance,
        description=bank_account.description,
        user_id=current_user.id,
    )

    session.add(new_account)
    session.commit()
    session.refresh(new_account)

    return new_account


# TRANSFERS
@router.get(f"{TRANSFERS_PREFIX}")
async def get_transfer_history(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    transfers = session.exec(
        select(Transfer).where(
            Transfer.sender_id == current_user.id,
            Transfer.receiver_id == current_user.id,
        )
    ).all()

    return transfers


@router.post(f"{TRANSFERS_PREFIX}")
async def make_transfer(
    transfer: TransferCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    sender_account = session.exec(
        select(BankAccount).where(BankAccount.user_id == current_user.id)
    ).first()

    receiver_account = session.exec(
        select(BankAccount).where(
            BankAccount.user_id == transfer.receiver_id
            and BankAccount.account_number == transfer.account_number
        )
    ).first()

    if not sender_account:
        raise HTTPException(status_code=404, detail="Sender account not found")

    if not receiver_account:
        raise HTTPException(status_code=404, detail="Receiver account not found")

    if sender_account.balance < transfer.balance:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    if transfer.balance <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be positive")

    if transfer.receiver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot transfer to self")

    sender_account.balance -= transfer.balance
    receiver_account.balance += transfer.balance

    transfer = Transfer(
        sender_id=current_user.id,
        receiver_id=receiver_account.user_id,
        balance=transfer.balance,
    )

    session.add(transfer)
    session.add(sender_account)
    session.add(receiver_account)
    session.commit()
    session.refresh(transfer)
    session.refresh(sender_account)
    session.refresh(receiver_account)

    return {
        "sender": sender_account,
        "receiver": receiver_account,
        "balance": transfer.balance,
    }


# CARDS
@router.get("/cards")
async def get_card_list(
    session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]
):
    cards = session.exec(
        select(Card).where(
            Card.account_id == BankAccount.id, User.id == current_user.id
        )
    ).all()

    return cards


# LOANS
@router.get("/loans")
async def get_loan_list(
    session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]
):
    loans = session.exec(select(Loan).where(Loan.user_id == current_user.id)).all()

    return loans


@router.get("/loans/{loan_id}")
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


@router.post("/loans")
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
