from typing import Annotated, Any
from fastapi import Depends
from sqlmodel import Session
from src.db.connection import SessionDep
from src.models.cards import CardResponseModel
from src.models.transfers import TransferResponseModel
from src.models.users import User, UserHomebankingInfo, UserResponseModel
from src.repositories.account_repository import AccountRepository
from src.repositories.card_repository import CardRepository
from src.repositories.transfer_repository import TransferRepository
from src.repositories.user_repository import UserRepository


class HomebankingService:
    def __init__(self, session: Session):
        self.session = session
        self.account_repo = AccountRepository(session)
        self.card_repo = CardRepository(session)
        self.transfer_repo = TransferRepository(session)
        self.user_repo = UserRepository(session)

    def get_dashboard(self, current_user: User) -> dict[str, Any]:
        bank_account = self.account_repo.get_primary_itbank_account(current_user.id)
        if not bank_account:
            accounts = self.account_repo.get_user_accounts(current_user.id)
            bank_account = accounts[0] if accounts else None

        cards = self.card_repo.get_user_cards(current_user.id)
        cards_response = [
            CardResponseModel(
                account_id=card.account_id,
                card_type=card.card_type,
                last_four=card.last_four,
                card_holder_name=card.card_holder_name,
                expiration_date=card.expiration_date,
                brand=card.brand,
                status=card.status,
                id=card.id,
            )
            for card in cards
        ]

        transfers = self.transfer_repo.get_user_sent_transfers_with_receiver(
            current_user.id
        )
        transfers_response = [
            TransferResponseModel(
                id=transfer.id,
                sender_username=current_user.username,
                receiver_username=user.username,
                balance=transfer.balance,
                transfer_date=transfer.transfer_date,
                transfer_type=transfer.transfer_type,
            )
            for transfer, user in transfers
        ]

        return {
            "user": UserHomebankingInfo(
                email=current_user.email,
                full_name=current_user.full_name,
                username=current_user.username,
            ),
            "itbank_account": bank_account,
            "cards": cards_response,
            "transfers": transfers_response,
        }

    def get_all_users(self) -> list[UserResponseModel]:
        users = self.user_repo.list_all()
        return [
            UserResponseModel(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                username=user.username,
            )
            for user in users
        ]


def get_homebanking_service(session: SessionDep) -> HomebankingService:
    return HomebankingService(session)


HomebankingServiceDep = Annotated[HomebankingService, Depends(get_homebanking_service)]
