from coolname import generate_slug
import uuid
from typing import Annotated
from faker import Faker
from fastapi import Depends


def get_bank_alias(username: str) -> str:
    return f"{username}.{generate_slug(3).replace('-', '.')}"


def generate_account_number():
    return str(uuid.uuid4().hex[:16].upper())


fake = Faker(locale="es_AR")
FakerDep = Annotated[Faker, Depends(lambda: fake)]
