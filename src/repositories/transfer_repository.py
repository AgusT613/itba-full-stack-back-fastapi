from sqlmodel import Session, select
from sqlalchemy.orm import aliased
from src.models.transfers import Transfer
from src.models.users import User
from src.repositories.base import BaseRepository


class TransferRepository(BaseRepository[Transfer]):
    def __init__(self, session: Session):
        super().__init__(session, Transfer)

    def get_user_transfer_history(self, user_id: int):
        Sender = aliased(User)
        Receiver = aliased(User)

        statement = (
            select(Transfer, Sender, Receiver)
            .join(Sender, Transfer.sender_id == Sender.id)
            .join(Receiver, Transfer.receiver_id == Receiver.id)
            .where(
                (Transfer.sender_id == user_id) | (Transfer.receiver_id == user_id)
            )
        )
        return list(self.session.exec(statement).all())

    def get_user_sent_transfers_with_receiver(self, user_id: int):
        statement = (
            select(Transfer, User)
            .join(User, onclause=Transfer.receiver_id == User.id)
            .where(Transfer.sender_id == user_id)
        )
        return list(self.session.exec(statement).all())

    def get_user_transfer(self, transfer_id: int, user_id: int) -> Transfer | None:
        statement = select(Transfer).where(
            Transfer.id == transfer_id,
            Transfer.sender_id == user_id,
        )
        return self.session.exec(statement).first()
