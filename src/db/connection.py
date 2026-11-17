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
    """Dispose of engine connection pool on application shutdown.

    Preserves persistent database data across container restarts and server redeployments.
    Table dropping or SQLite file deletion is only performed if PURGE_DATABASE_ON_SHUTDOWN
    is explicitly set to 'true' (e.g., ephemeral test environments or transient pipelines).
    """
    try:
        purge_on_shutdown = (
            os.getenv("PURGE_DATABASE_ON_SHUTDOWN", "false").lower() in ("true", "1")
        )
        if purge_on_shutdown:
            if DATABASE_URL.startswith("sqlite:///"):
                db_path = DATABASE_URL.replace("sqlite:///", "")
                engine.dispose()
                if os.path.exists(db_path):
                    os.remove(db_path)
            else:
                drop_db_and_tables()
                engine.dispose()
        else:
            engine.dispose()
    except Exception as e:
        print(f"Error during database shutdown cleanup: {e}")


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
