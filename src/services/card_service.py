from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.exceptions.banking_exceptions import EntityNotFoundError, InvalidOperationError
from src.models.cards import (
    Card,
    CardCreate,
    CardPartialUpdate,
    CardFullUpdate,
    CardResponseModel,
)
from src.repositories.account_repository import AccountRepository
from src.repositories.card_repository import CardRepository
from src.utils.password import get_password_hash


class CardService:
    def __init__(self, session: Session):
        self.session = session
        self.card_repo = CardRepository(session)
        self.account_repo = AccountRepository(session)

    @staticmethod
    def _to_response_model(card: Card) -> CardResponseModel:
        return CardResponseModel(
            id=card.id,
            account_id=card.account_id,
            card_type=card.card_type,
            last_four=card.last_four,
            card_holder_name=card.card_holder_name,
            expiration_date=card.expiration_date,
            brand=card.brand,
            status=card.status,
        )

    def get_cards(self, user_id: int) -> list[CardResponseModel]:
        cards = self.card_repo.get_user_cards(user_id)
        return [self._to_response_model(c) for c in cards]

    def get_card_details(self, card_id: int, user_id: int) -> CardResponseModel:
        card = self.card_repo.get_user_card(card_id, user_id)
        if not card:
            raise EntityNotFoundError("Card not found")
        return self._to_response_model(card)

    def create_card(self, user_id: int, card_in: CardCreate) -> CardResponseModel:
        account = self.account_repo.get_by_id(card_in.account_id)
        if not account or account.user_id != user_id:
            raise InvalidOperationError("Invalid account ID")

        new_card = Card(
            user_id=user_id,
            account_id=account.id,
            card_type=card_in.card_type,
            last_four=card_in.last_four,
            card_holder_name=card_in.card_holder_name,
            expiration_date=card_in.expiration_date,
            brand=card_in.brand,
            status=card_in.status,
            hashed_pin=get_password_hash(card_in.pin),
        )

        self.card_repo.add(new_card)
        self.card_repo.commit()
        self.card_repo.refresh(new_card)
        return self._to_response_model(new_card)

    def update_card_partially(
        self,
        card_id: int,
        user_id: int,
        card_update: CardPartialUpdate,
    ) -> CardResponseModel:
        card = self.card_repo.get_user_card(card_id, user_id)
        if not card:
            raise EntityNotFoundError("Card not found")

        for key, value in card_update.model_dump(exclude_unset=True).items():
            setattr(card, key, value)

        self.card_repo.add(card)
        self.card_repo.commit()
        self.card_repo.refresh(card)
        return self._to_response_model(card)

    def update_card_fully(
        self,
        card_id: int,
        user_id: int,
        card_update: CardFullUpdate,
    ) -> CardResponseModel:
        card = self.card_repo.get_user_card(card_id, user_id)
        if not card:
            raise EntityNotFoundError("Card not found")

        for key, value in card_update.model_dump(exclude_unset=True).items():
            setattr(card, key, value)

        self.card_repo.add(card)
        self.card_repo.commit()
        self.card_repo.refresh(card)
        return self._to_response_model(card)

    def delete_card(self, card_id: int, user_id: int) -> CardResponseModel:
        card = self.card_repo.get_user_card(card_id, user_id)
        if not card:
            raise EntityNotFoundError("Card not found")

        self.card_repo.delete(card)
        self.card_repo.commit()
        return self._to_response_model(card)


def get_card_service(session: SessionDep) -> CardService:
    return CardService(session)


CardServiceDep = Annotated[CardService, Depends(get_card_service)]
