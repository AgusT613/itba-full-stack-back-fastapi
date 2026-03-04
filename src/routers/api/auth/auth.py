from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends
from src.lib.generate_account_number import generate_account_number
from src.models.users import User
from src.models.accounts import BankAccount
from fastapi.security import OAuth2PasswordRequestForm
from src.db.connection import SessionDep
from datetime import timedelta
from src.constants.constants import (
    ALREADY_REGISTERED_USER,
    AUTH_POST_REGISTER,
    AUTH_POST_TOKEN,
    AUTH_PREFIX,
    INCORRECT_USERNAME_OR_PASSWORD,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from src.lib.auth_utils import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_user,
)
from src.models.auth import Token, UserModel
from src.lib.generate_alias import get_bank_alias


router = APIRouter(prefix=AUTH_PREFIX)


@router.post(AUTH_POST_TOKEN)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)

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


@router.post(AUTH_POST_REGISTER, status_code=status.HTTP_201_CREATED)
async def register(
    user: UserModel,
    session: SessionDep,
):
    user_found = get_user(session, username=user.username)

    if user_found:
        raise HTTPException(status_code=400, detail=ALREADY_REGISTERED_USER)

    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email="",
        full_name="",
        hashed_password=hashed_password,
        disabled=False,
    )

    session.add(new_user)
    session.flush()

    new_account = BankAccount(
        description="ITBANK account",
        account_number=generate_account_number(),
        account_type="itbank",
        balance=0.0,
        user_id=new_user.id,
        alias=get_bank_alias(user.username),
    )

    session.add(new_account),
    session.commit()
    session.refresh(new_user)
    session.refresh(new_account)

    return {"user": new_user, "bank_account": new_account}
