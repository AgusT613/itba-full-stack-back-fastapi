from typing import Annotated
from faker import Faker
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import (
    DuplicateResourceError,
    EntityNotFoundError,
)
from src.models.branch_offices import BranchOffice
from src.repositories.branch_repository import BranchRepository


class BranchService:
    def __init__(self, session: Session):
        self.session = session
        self.branch_repo = BranchRepository(session)

    def list_branch_offices(self) -> list[BranchOffice]:
        return self.branch_repo.list_all()

    def create_branch_office(self, fake: Faker) -> BranchOffice:
        name = fake.company()
        if self.branch_repo.get_by_name(name):
            raise DuplicateResourceError("Branch office already exists")

        new_branch_office = BranchOffice(
            name=name,
            address=fake.address(),
            contact=fake.phone_number(),
        )

        self.branch_repo.add(new_branch_office)
        self.branch_repo.commit()
        self.branch_repo.refresh(new_branch_office)
        return new_branch_office

    def delete_branch_office(self, branch_office_id: int) -> BranchOffice:
        branch = self.branch_repo.get_by_id(branch_office_id)
        if not branch:
            raise EntityNotFoundError("Branch office not found")

        self.branch_repo.delete(branch)
        self.branch_repo.commit()
        return branch


def get_branch_service(session: SessionDep) -> BranchService:
    return BranchService(session)


BranchServiceDep = Annotated[BranchService, Depends(get_branch_service)]
