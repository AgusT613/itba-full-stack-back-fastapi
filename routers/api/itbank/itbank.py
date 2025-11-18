from fastapi import APIRouter
from db.connection import SessionDep
from sqlmodel import select
from models.branch_office import BranchOffice

router = APIRouter(prefix="/itbank")


@router.get("/")
async def read_root():
    return {"Hello": "Homebanking"}


@router.get("/branch-offices")
async def read_item(session: SessionDep):
    return session.exec(select(BranchOffice)).all()
