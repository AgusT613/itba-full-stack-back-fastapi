from sqlmodel import Session, select
from src.models.cards import Card
from src.repositories.base import BaseRepository


class CardRepository(BaseRepository[Card]):
    def __init__(self, session: Session):
        super().__init__(session, Card)

    def get_user_cards(self, user_id: int) -> list[Card]:
        statement = select(Card).where(Card.user_id == user_id)
        return list(self.session.exec(statement).all())

    def get_user_card(self, card_id: int, user_id: int) -> Card | None:
        statement = select(Card).where(
            Card.id == card_id,
            Card.user_id == user_id,
        )
        return self.session.exec(statement).first()
