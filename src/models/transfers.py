from datetime import datetime
from sqlmodel import SQLModel, Field, func
from pydantic import BaseModel


class Transfer(SQLModel, table=True):
    __tablename__ = "transfers"

    id: int | None = Field(default=None, primary_key=True)
    sender_id: int = Field(foreign_key="users.id")
    receiver_id: int = Field(foreign_key="users.id")
    balance: float = Field(default=0.0)
    transfer_date: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, nullable=False
    )


class TransferCreate(BaseModel):
    sender_id: int
    receiver_id: int
    account_number: str
    balance: float
