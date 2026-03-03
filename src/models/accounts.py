from sqlmodel import SQLModel, Field
from src.constants.constants import BANK_ACCOUNTS
from pydantic import BaseModel


class BankAccount(SQLModel, table=True):
    __tablename__ = BANK_ACCOUNTS

    id: int | None = Field(default=None, primary_key=True)
    account_type: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=255)
    balance: float
    account_number: str = Field(max_length=20)
    alias: str = Field(max_length=50, unique=True)

    user_id: int = Field(foreign_key="users.id")


class BankAccountCreate(BaseModel):
    account_type: str
    description: str
    balance: float
    account_number: str


class BankAccountPartialUpdate(BaseModel):
    account_number: str
    account_type: str | None = None
    description: str | None = None
    balance: float | None = None
    alias: str | None = None


class BankAccountFullUpdate(BaseModel):
    account_number: str
    account_type: str
    description: str
    balance: float
    alias: str
