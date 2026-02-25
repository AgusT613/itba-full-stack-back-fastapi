from sqlmodel import Field, SQLModel
from src.constants.constants import BRANCH_OFFICES
from pydantic import BaseModel


class BranchOffice(SQLModel, table=True):
    __tablename__ = BRANCH_OFFICES
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: str = Field(max_length=255)
    contact: str = Field(max_length=15, nullable=True)


class BranchOfficeCreate(BaseModel):
    name: str
    address: str
    contact: str
