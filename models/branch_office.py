from sqlmodel import Field, SQLModel
from constants.constants import BRANCH_OFFICE


class BranchOffice(SQLModel, table=True):
    __tablename__ = BRANCH_OFFICE
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: str = Field(max_length=255)
    contact: str = Field(max_length=15, nullable=True)
