from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends
from models.user import User
from fastapi.security import OAuth2PasswordRequestForm
from db.connection import SessionDep
from datetime import timedelta
from constants.constants import (
    ALREADY_REGISTERED_USER,
    AUTH_GET_CURRENT_ACTIVE_USER,
    AUTH_GET_CURRENT_USER,
    AUTH_POST_REGISTER,
    AUTH_POST_TOKEN,
    AUTH_PREFIX,
    INCORRECT_USERNAME_OR_PASSWORD,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from routers.api.auth.utils import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    get_current_user,
    get_password_hash,
    get_user,
)
from routers.api.auth.schemas import Token, UserModel


router = APIRouter(prefix=AUTH_PREFIX)


@router.get(AUTH_GET_CURRENT_USER)
async def read_current_user(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user


@router.get(AUTH_GET_CURRENT_ACTIVE_USER)
async def read_current_active_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"owner": current_user.username, "info": current_user}]


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


@router.post(AUTH_POST_REGISTER)
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
    session.commit()
    session.refresh(new_user)

    return new_user
