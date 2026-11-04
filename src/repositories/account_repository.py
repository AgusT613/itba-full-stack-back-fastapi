from sqlmodel import Session, select
from src.models.accounts import BankAccount
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository[BankAccount]):
    def __init__(self, session: Session):
        super().__init__(session, BankAccount)

    def get_user_accounts(self, user_id: int) -> list[BankAccount]:
        statement = select(BankAccount).where(BankAccount.user_id == user_id)
        return list(self.session.exec(statement).all())

    def get_by_alias(self, alias: str) -> BankAccount | None:
        statement = select(BankAccount).where(BankAccount.alias == alias)
        return self.session.exec(statement).first()

    def get_user_account_by_alias(self, user_id: int, alias: str) -> BankAccount | None:
        statement = select(BankAccount).where(
            BankAccount.user_id == user_id,
            BankAccount.alias == alias,
        )
        return self.session.exec(statement).first()

    def get_user_account_by_identifier(
        self,
        user_id: int,
        acc_number: str | None = None,
        acc_id: int | None = None,
        acc_alias: str | None = None,
    ) -> BankAccount | None:
        conditions = []
        if acc_number is not None:
            conditions.append(BankAccount.account_number == acc_number)
        if acc_id is not None:
            conditions.append(BankAccount.id == acc_id)
        if acc_alias is not None:
            conditions.append(BankAccount.alias == acc_alias)

        if not conditions:
            return None

        # Matches if any of provided identifiers match AND user_id matches
        from sqlalchemy import or_

        statement = select(BankAccount).where(
            or_(*conditions),
            BankAccount.user_id == user_id,
        )
        return self.session.exec(statement).first()

    def get_primary_itbank_account(self, user_id: int) -> BankAccount | None:
        statement = select(BankAccount).where(
            BankAccount.user_id == user_id,
            BankAccount.account_type == "itbank",
        )
        return self.session.exec(statement).first()
