from typing import Annotated
from faker import Faker
from fastapi import Depends
from sqlmodel import Session

from src.db.connection import get_session

fake = Faker(locale="es_AR")

FakerDep = Annotated[Faker, Depends(lambda: fake)]
SessionDep = Annotated[Session, Depends(get_session)]
