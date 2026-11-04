from sqlmodel import Session, select
from src.models.user_saved_aliases import UserSavedAlias
from src.repositories.base import BaseRepository


class AliasRepository(BaseRepository[UserSavedAlias]):
    def __init__(self, session: Session):
        super().__init__(session, UserSavedAlias)

    def get_user_saved_aliases(self, user_id: int) -> list[UserSavedAlias]:
        statement = select(UserSavedAlias).where(UserSavedAlias.user_id == user_id)
        return list(self.session.exec(statement).all())

    def get_by_alias(self, alias: str) -> UserSavedAlias | None:
        statement = select(UserSavedAlias).where(UserSavedAlias.alias == alias)
        return self.session.exec(statement).first()

    def get_user_saved_alias(self, user_id: int, alias: str) -> UserSavedAlias | None:
        statement = select(UserSavedAlias).where(
            UserSavedAlias.user_id == user_id,
            UserSavedAlias.alias == alias,
        )
        return self.session.exec(statement).first()
