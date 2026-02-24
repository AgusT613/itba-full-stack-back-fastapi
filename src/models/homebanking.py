from pydantic import BaseModel
from .cards import CardResponseModel
from .transfers import TransferResponseModel


class HomebankingInit(BaseModel):
    username: str
    balance: float
    cards: list[CardResponseModel]
    transfers: list[TransferResponseModel]
