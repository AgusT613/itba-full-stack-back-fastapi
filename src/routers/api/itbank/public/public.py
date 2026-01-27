from fastapi import APIRouter
from src.constants.constants import ITBANK_BRANCH_OFFICES, ITBANK_PREFIX
from src.db.connection import SessionDep
from sqlmodel import select
from src.models.branch_offices import BranchOffice

router = APIRouter(prefix=ITBANK_PREFIX)


@router.get(ITBANK_BRANCH_OFFICES)
async def read_item(session: SessionDep):
    return session.exec(select(BranchOffice)).all()
