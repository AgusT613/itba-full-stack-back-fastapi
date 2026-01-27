from fastapi import APIRouter
from .public.public import router as public_router
from .homebanking.homebanking import router as homebanking_router

router = APIRouter()

router.include_router(public_router)
router.include_router(homebanking_router)
