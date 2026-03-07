from fastapi import APIRouter
from src.constants.constants import API_PREFIX
from src.routers.api.itbank import itbank
from src.routers.api.auth import auth

api_router = APIRouter(prefix=API_PREFIX)

api_router.include_router(itbank.router)
api_router.include_router(auth.router)
