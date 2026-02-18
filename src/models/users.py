from sqlmodel import SQLModel, Field
from src.constants.constants import USERS


class User(SQLModel, table=True):
    __tablename__ = USERS
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=255)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=255)
    disabled: bool
    hashed_password: str
