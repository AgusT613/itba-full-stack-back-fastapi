from fastapi import APIRouter, HTTPException, status
from typing import Annotated
from fastapi import Depends
from models.user import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db.connection import SessionDep
from sqlmodel import select
from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
import jwt
from jwt.exceptions import InvalidTokenError
from constants.constants import (
    ALREADY_REGISTERED_USER,
    AUTH_GET_CURRENT_ACTIVE_USER,
    AUTH_GET_CURRENT_USER,
    AUTH_POST_REGISTER,
    AUTH_POST_TOKEN,
    AUTH_PREFIX,
    INCORRECT_USERNAME_OR_PASSWORD,
    INVALIDE_CREDENTIALS,
    INACTIVE_USER,
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    TOKEN_URL,
)

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)
router = APIRouter(prefix=AUTH_PREFIX)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password, hashed_password):
    return password_hash.verify(plain_password, hashed_password)


def get_password_hash(password):
    return password_hash.hash(password)


def get_user(session: SessionDep, username: str):
    user = session.exec(select(User).where(User.username == username)).first()

    return user


def authenticate_user(session: SessionDep, username: str, password: str):
    user = get_user(session, username)

    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=INVALIDE_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise credentials_exception

        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception

    user = get_user(session, username=token_data.username)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail=INACTIVE_USER)

    return current_user


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


class UserModel(BaseModel):
    username: str
    password: str


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
