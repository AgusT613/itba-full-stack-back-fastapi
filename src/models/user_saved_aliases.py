from sqlmodel import SQLModel, Field


class UserSavedAlias(SQLModel, table=True):
    __tablename__ = "user_saved_aliases"

    id: int = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    alias: str
