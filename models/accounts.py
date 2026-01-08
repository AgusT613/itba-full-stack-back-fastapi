from sqlmodel import SQLModel, Field


class BankAccount(SQLModel, table=True):
    __tablename__ = "bank_account"

    account_type: str = Field(max_length=50)
    description: str | None = Field(default=None, max_length=255)
    balance: float
    account_number: str = Field(max_length=20, primary_key=True)

    user_id: int = Field(foreign_key="user.id")
