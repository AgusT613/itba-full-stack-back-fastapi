from sqlmodel import SQLModel, Field
from constants.constants import BANK_ACCOUNTS


class BankAccount(SQLModel, table=True):
    __tablename__ = BANK_ACCOUNTS

    account_type: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=255)
    balance: float
    account_number: str = Field(max_length=20, primary_key=True)

    user_id: int = Field(foreign_key="users.id")
