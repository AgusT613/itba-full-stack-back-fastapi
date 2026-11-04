from sqlmodel import Session
from src.models.users import User
from src.repositories.user_repository import UserRepository


def get_user(session: Session, username: str) -> User | None:
    return UserRepository(session).get_by_username(username)
