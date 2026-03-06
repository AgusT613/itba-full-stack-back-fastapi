from pydantic import BaseModel
from src.models.users import UserBase
from src.models.accounts import BankAccount


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RegisterResponse(BaseModel):
    user: UserBase
    bank_account: BankAccount
