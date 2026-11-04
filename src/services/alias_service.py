from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import (
    DuplicateResourceError,
    EntityNotFoundError,
)
from src.models.user_saved_aliases import UserSavedAlias, UserSavedAliasResponseModel
from src.repositories.account_repository import AccountRepository
from src.repositories.alias_repository import AliasRepository


class AliasService:
    def __init__(self, session: Session):
        self.session = session
        self.alias_repo = AliasRepository(session)
        self.account_repo = AccountRepository(session)

    def get_all_account_aliases(self, user_id: int) -> list[dict[str, str]]:
        accounts = self.account_repo.get_user_accounts(user_id)
        if not accounts:
            raise EntityNotFoundError("No accounts found")
        return [{"alias": account.alias} for account in accounts]

    def get_itbank_alias(self, user_id: int) -> dict[str, str]:
        account = self.account_repo.get_primary_itbank_account(user_id)
        if not account:
            raise EntityNotFoundError("ITBANK account not found")
        return {"alias": account.alias}

    def get_saved_aliases(self, user_id: int) -> list[UserSavedAliasResponseModel]:
        aliases = self.alias_repo.get_user_saved_aliases(user_id)
        if not aliases:
            raise EntityNotFoundError("No saved aliases found")
        return [
            UserSavedAliasResponseModel(id=alias.id, alias=alias.alias)
            for alias in aliases
        ]

    def save_alias(self, user_id: int, alias_str: str) -> UserSavedAliasResponseModel:
        account = self.account_repo.get_by_alias(alias_str)
        if not account:
            raise EntityNotFoundError("Account with alias not found")

        existing_alias = self.alias_repo.get_by_alias(alias_str)
        if existing_alias:
            raise DuplicateResourceError("Alias already saved")

        new_alias = UserSavedAlias(user_id=user_id, alias=account.alias)
        self.alias_repo.add(new_alias)
        self.alias_repo.commit()
        self.alias_repo.refresh(new_alias)
        return UserSavedAliasResponseModel(id=new_alias.id, alias=new_alias.alias)


def get_alias_service(session: SessionDep) -> AliasService:
    return AliasService(session)


AliasServiceDep = Annotated[AliasService, Depends(get_alias_service)]
