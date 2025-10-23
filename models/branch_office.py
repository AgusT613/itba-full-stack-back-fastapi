from sqlmodel import Field, SQLModel


class BranchOffice(SQLModel, table=True):
    __tablename__ = "branch_office"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=255)
    address: str = Field(max_length=255)
    contact: str = Field(max_length=15, nullable=True)
