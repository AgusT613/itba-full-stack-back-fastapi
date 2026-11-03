from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.models.users import User
from src.db.connection import SessionDep
from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError
from src.constants.constants import (
    INACTIVE_USER,
    INVALIDE_CREDENTIALS,
    SECRET_KEY,
    ALGORITHM,
    TOKEN_URL,
)
from src.models.auth import TokenData
from src.db.user import get_user
from .password import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=TOKEN_URL)


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


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_current_active_user(
    current_user: CurrentUserDep,
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail=INACTIVE_USER)

    return current_user
