from fastapi import APIRouter, Depends
from constants.constants import HOME_BANKING_PREFIX
from routers.api.auth.utils import get_current_user


router = APIRouter(prefix=HOME_BANKING_PREFIX, dependencies=[Depends(get_current_user)])


@router.get("/")
async def read_homebanking():
    return {"message": "Welcome to Home Banking!"}
