from pydantic import BaseModel
from src.models.users import UserResponseModel
from src.models.accounts import BankAccount


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class RegisterResponse(UserResponseModel, BankAccount):
    pass
