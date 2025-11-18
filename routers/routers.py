from fastapi import APIRouter
from constants.constants import API_PREFIX
from routers.api.itbank import itbank
from routers.api.auth import auth

api_router = APIRouter(prefix=API_PREFIX)

api_router.include_router(itbank.router)
api_router.include_router(auth.router)
