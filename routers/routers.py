from fastapi import APIRouter
from routers.api.itbank import itbank
from routers.api.auth import auth

api_router = APIRouter(prefix="/api")

api_router.include_router(itbank.router, tags=["itbank"])
api_router.include_router(auth.router, tags=["auth"])
