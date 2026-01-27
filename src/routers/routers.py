from fastapi import APIRouter
from src.constants.constants import API_PREFIX, AUTH_ROUTER_TAG, ITBANK_ROUTER_TAG
from src.routers.api.itbank import itbank
from src.routers.api.auth import auth

api_router = APIRouter(prefix=API_PREFIX)

api_router.include_router(itbank.router, tags=[ITBANK_ROUTER_TAG])
api_router.include_router(auth.router, tags=[AUTH_ROUTER_TAG])
