from sqlmodel import SQLModel, Field
from src.constants.constants import USERS


class UserBase(SQLModel):
    username: str = Field(max_length=255)
    # TODO: Add unique constraint to email and remove default value
    email: str = Field(max_length=255, default="")
    full_name: str = Field(max_length=255, default="")


class User(UserBase, table=True):
    __tablename__ = USERS

    id: int | None = Field(default=None, primary_key=True)
    disabled: bool
    hashed_password: str


class UserRegister(SQLModel):
    username: str
    password: str
    email: str | None = None
    full_name: str | None = None


class UserHomebankingInfo(UserBase):
    pass


class UserResponseModel(UserBase):
    id: int
