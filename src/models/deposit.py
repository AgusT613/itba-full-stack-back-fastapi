from pydantic import BaseModel


class DepositCreate(BaseModel):
    amount: float
    alias: str
