from .connection import SessionDep
from sqlmodel import select
from src.models.users import User


def get_user(session: SessionDep, username: str):
    user = session.exec(select(User).where(User.username == username)).first()

    return user
