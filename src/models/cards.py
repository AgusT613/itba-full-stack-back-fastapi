from sqlmodel import SQLModel, Field, func
from datetime import datetime


class Card(SQLModel, table=True):
    __tablename__ = "cards"

    id: int | None = Field(default=None, primary_key=True)
    account_id: int = Field(foreign_key="bank_accounts.id")
    user_id: int = Field(foreign_key="users.id")
    card_type: str
    last_four: str
    card_holder_name: str
    expiration_date: datetime
    brand: str
    status: str
    hashed_pin: str
    created_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
    updated_at: datetime = Field(
        sa_column_kwargs={"server_default": func.now()}, nullable=False
    )
