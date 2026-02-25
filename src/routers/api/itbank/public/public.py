from fastapi import APIRouter, HTTPException, status
from src.constants.constants import ITBANK_BRANCH_OFFICES, ITBANK_PREFIX
from src.db.connection import SessionDep
from sqlmodel import select
from src.models.branch_offices import BranchOffice
from faker import Faker

router = APIRouter(prefix=ITBANK_PREFIX)
fake = Faker(locale="es_AR")


@router.get(ITBANK_BRANCH_OFFICES)
async def read_item(session: SessionDep):
    return session.exec(select(BranchOffice)).all()


@router.post(ITBANK_BRANCH_OFFICES)
async def create_branch_office(session: SessionDep):
    new_branch_office = BranchOffice(
        name=fake.company(),
        address=fake.address(),
        contact=fake.phone_number(),
    )

    branch_office_exist = session.exec(
        select(BranchOffice).where(BranchOffice.name == new_branch_office.name)
    ).first()

    if branch_office_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Branch office already exists",
        )

    session.add(new_branch_office)
    session.commit()
    session.refresh(new_branch_office)
    return new_branch_office


@router.delete(f"{ITBANK_BRANCH_OFFICES}/{{branch_office_id}}")
async def delete_branch_office(branch_office_id: int, session: SessionDep):
    branch_office = session.exec(
        select(BranchOffice).where(BranchOffice.id == branch_office_id)
    ).first()

    if not branch_office:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Branch office not found",
        )

    session.delete(branch_office)
    session.commit()
    return {
        "detail": "Branch office deleted successfully",
        "deleted_branch_office": branch_office,
    }
