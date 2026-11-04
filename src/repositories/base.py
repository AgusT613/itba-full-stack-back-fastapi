from typing import Generic, TypeVar, Any
from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: Session, model: type[T]):
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: Any) -> T | None:
        return self.session.get(self.model, entity_id)

    def list_all(self) -> list[T]:
        statement = select(self.model)
        return list(self.session.exec(statement).all())

    def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    def delete(self, entity: T) -> None:
        self.session.delete(entity)

    def commit(self) -> None:
        self.session.commit()

    def refresh(self, entity: T) -> T:
        self.session.refresh(entity)
        return entity

    def flush(self) -> None:
        self.session.flush()
