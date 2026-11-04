from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from src.constants.constants import (
    AUTH_POST_REGISTER,
    AUTH_POST_TOKEN,
    AUTH_PREFIX,
)
from src.models.auth import RegisterResponse, Token
from src.models.users import UserRegister
from src.services.auth_service import AuthServiceDep

router = APIRouter(prefix=AUTH_PREFIX, tags=["auth"])


@router.post(AUTH_POST_TOKEN, response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: AuthServiceDep,
):
    return auth_service.authenticate_and_create_token(
        form_data.username, form_data.password
    )


@router.post(
    AUTH_POST_REGISTER,
    status_code=status.HTTP_201_CREATED,
    response_model=RegisterResponse,
)
async def register(
    user: UserRegister,
    auth_service: AuthServiceDep,
):
    return auth_service.register_user(user)
