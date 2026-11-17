import os
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from src.constants.constants import DATABASE_URL, ENVIRONMENT

is_sqlite = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True if not is_sqlite else False,
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def drop_db_and_tables():
    SQLModel.metadata.drop_all(engine)


def cleanup_prod_database():
    """Tear down and clean up production database when shutting down."""
    if ENVIRONMENT in ("production", "prod"):
        try:
            engine.dispose()
            if DATABASE_URL.startswith("sqlite:///"):
                db_path = DATABASE_URL.replace("sqlite:///", "")
                if os.path.exists(db_path):
                    os.remove(db_path)
            else:
                drop_db_and_tables()
        except Exception as e:
            print(f"Error during production database cleanup: {e}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
