from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    username: str = Field(max_length=255)
    email: str = Field(max_length=255)
    full_name: str = Field(max_length=255)
    disabled: bool
    hashed_password: str
