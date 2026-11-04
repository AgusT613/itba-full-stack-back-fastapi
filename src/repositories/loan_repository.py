from sqlmodel import Session, select
from src.models.loans import Loan
from src.repositories.base import BaseRepository


class LoanRepository(BaseRepository[Loan]):
    def __init__(self, session: Session):
        super().__init__(session, Loan)

    def get_user_loans(self, user_id: int) -> list[Loan]:
        statement = select(Loan).where(Loan.user_id == user_id)
        return list(self.session.exec(statement).all())

    def get_user_loan(self, loan_id: int, user_id: int) -> Loan | None:
        statement = select(Loan).where(
            Loan.id == loan_id,
            Loan.user_id == user_id,
        )
        return self.session.exec(statement).first()
