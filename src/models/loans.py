from sqlmodel import SQLModel, Field, func
from datetime import datetime
from pydantic import BaseModel


class Loan(SQLModel, table=True):
    __tablename__ = "loans"

    id: int = Field(default=None, primary_key=True)
    branch_office_id: int = Field(foreign_key="branch_offices.id")
    user_id: int = Field(foreign_key="users.id")
    user_account_id: int = Field(foreign_key="bank_accounts.user_id")
    loan_type: str
    start_date: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
    due_date: float
    amount: float
    status: str
    interest_rate: float
    total_repayment: float
    total_installments: int
    remaining_installments: int


class LoanCreate(BaseModel):
    branch_office_id: int
    user_account_id: int
    loan_type: str
    due_date: float
    amount: float
    interest_rate: float
    total_installments: int
    remaining_installments: int


class LoanPartialUpdate(BaseModel):
    branch_office_id: int | None = None
    user_account_id: int | None = None
    loan_type: str | None = None
    status: str | None = None
    remaining_installments: int | None = None


class LoanFullUpdate(BaseModel):
    branch_office_id: int
    user_account_id: int
    loan_type: str
    status: str
    remaining_installments: int
