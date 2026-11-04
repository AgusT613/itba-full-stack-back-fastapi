from datetime import timedelta
from typing import Annotated, Any
from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from src.constants.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALREADY_REGISTERED_USER,
    INCORRECT_USERNAME_OR_PASSWORD,
)
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import DuplicateResourceError
from src.models.accounts import BankAccount
from src.models.auth import Token
from src.models.users import User, UserRegister
from src.repositories.account_repository import AccountRepository
from src.repositories.user_repository import UserRepository
from src.utils.auth_user import authenticate_user, create_access_token
from src.utils.password import get_password_hash
from src.utils.text_generation import generate_account_number, get_bank_alias


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
        self.account_repo = AccountRepository(session)

    def authenticate_and_create_token(self, username: str, password: str) -> Token:
        user = authenticate_user(self.session, username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INCORRECT_USERNAME_OR_PASSWORD,
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")

    def register_user(self, user: UserRegister) -> dict[str, Any]:
        user_found = self.user_repo.get_by_username(user.username)
        if user_found:
            raise DuplicateResourceError(ALREADY_REGISTERED_USER)

        hashed_password = get_password_hash(user.password)
        new_user = User(
            username=user.username,
            email=user.email or "",
            full_name=user.full_name or "",
            hashed_password=hashed_password,
            disabled=False,
        )

        self.user_repo.add(new_user)
        self.user_repo.flush()

        new_account = BankAccount(
            description="ITBANK account",
            account_number=generate_account_number(),
            account_type="itbank",
            balance=0.0,
            user_id=new_user.id,
            alias=get_bank_alias(user.username),
        )

        self.account_repo.add(new_account)
        self.session.commit()
        self.user_repo.refresh(new_user)
        self.account_repo.refresh(new_account)

        return {
            **new_user.model_dump(),
            **new_account.model_dump(),
        }


def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
