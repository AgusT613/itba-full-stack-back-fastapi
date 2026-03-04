from sqlmodel import Session
from src.models.users import User
from src.lib.auth_utils import get_password_hash
from faker import Faker


def _create_user(
    session: Session,
    fake: Faker,
    username: str = None,
    password: str = None,
) -> User:
    username = username or fake.user_name()
    password = password or fake.password()

    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        disabled=False,
        email=fake.email(),
        full_name=fake.name(),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return user
