from sqlmodel import Session, select
from src.models.branch_offices import BranchOffice
from src.repositories.base import BaseRepository


class BranchRepository(BaseRepository[BranchOffice]):
    def __init__(self, session: Session):
        super().__init__(session, BranchOffice)

    def get_by_name(self, name: str) -> BranchOffice | None:
        statement = select(BranchOffice).where(BranchOffice.name == name)
        return self.session.exec(statement).first()
