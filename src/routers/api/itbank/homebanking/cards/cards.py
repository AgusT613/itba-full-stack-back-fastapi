from fastapi import APIRouter, Depends, HTTPException, status
from src.lib.auth_utils import get_current_user
from src.db.connection import SessionDep
from sqlmodel import select
from src.models.cards import (
    Card,
    CardCreate,
    CardPartialUpdate,
    CardFullUpdate,
    CardResponseModel,
)
from src.models.accounts import BankAccount
from src.models.users import User
from typing import Annotated
from src.lib.auth_utils import get_password_hash

router = APIRouter(prefix="/cards", dependencies=[Depends(get_current_user)])


@router.get("/")
async def get_card_list(
    session: SessionDep, current_user: Annotated[User, Depends(get_current_user)]
):
    cards = session.exec(select(Card).where(Card.user_id == current_user.id)).all()

    response = [
        CardResponseModel(
            id=card.id,
            account_id=card.account_id,
            card_type=card.card_type,
            last_four=card.last_four,
            card_holder_name=card.card_holder_name,
            expiration_date=card.expiration_date,
            brand=card.brand,
            status=card.status,
        )
        for card in cards
    ]

    return response


@router.get("/{card_id}")
async def get_card_details(
    card_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    card = session.exec(
        select(Card).where(
            Card.id == card_id,
            Card.account_id == BankAccount.id,
            User.id == current_user.id,
        )
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    response = CardResponseModel(
        id=card.id,
        account_id=card.account_id,
        card_type=card.card_type,
        last_four=card.last_four,
        card_holder_name=card.card_holder_name,
        expiration_date=card.expiration_date,
        brand=card.brand,
        status=card.status,
    )

    return response


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_card(
    card: CardCreate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    account = session.exec(
        select(BankAccount).where(BankAccount.id == card.account_id)
    ).first()

    if not account or account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account ID"
        )

    new_card = Card(
        user_id=current_user.id,
        account_id=account.id,
        card_type=card.card_type,
        last_four=card.last_four,
        card_holder_name=card.card_holder_name,
        expiration_date=card.expiration_date,
        brand=card.brand,
        status=card.status,
        hashed_pin=get_password_hash(card.pin),
    )

    session.add(new_card)
    session.commit()
    session.refresh(new_card)

    response = CardResponseModel(
        id=new_card.id,
        account_id=new_card.account_id,
        card_type=new_card.card_type,
        last_four=new_card.last_four,
        card_holder_name=new_card.card_holder_name,
        expiration_date=new_card.expiration_date,
        brand=new_card.brand,
        status=new_card.status,
    )

    return response


@router.patch("/{card_id}")
async def update_card(
    card_id: int,
    card_update: CardPartialUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    card = session.exec(
        select(Card).where(
            Card.id == card_id,
            Card.account_id == BankAccount.id,
            User.id == current_user.id,
        )
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    for key, value in card_update.model_dump(exclude_unset=True).items():
        setattr(card, key, value)

    session.add(card)
    session.commit()
    session.refresh(card)

    response = CardResponseModel(
        id=card.id,
        account_id=card.account_id,
        card_type=card.card_type,
        last_four=card.last_four,
        card_holder_name=card.card_holder_name,
        expiration_date=card.expiration_date,
        brand=card.brand,
        status=card.status,
    )

    return response


@router.put("/{card_id}")
async def replace_card(
    card_id: int,
    card_update: CardFullUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    card = session.exec(
        select(Card).where(
            Card.id == card_id,
            Card.account_id == BankAccount.id,
            User.id == current_user.id,
        )
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    for key, value in card_update.model_dump(
        exclude_unset=True,
    ).items():
        setattr(card, key, value)

    session.add(card)
    session.commit()
    session.refresh(card)

    response = CardResponseModel(
        id=card.id,
        account_id=card.account_id,
        card_type=card.card_type,
        last_four=card.last_four,
        card_holder_name=card.card_holder_name,
        expiration_date=card.expiration_date,
        brand=card.brand,
        status=card.status,
    )

    return response


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    card = session.exec(
        select(Card).where(
            Card.id == card_id,
            Card.account_id == BankAccount.id,
            User.id == current_user.id,
        )
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Card not found"
        )

    session.delete(card)
    session.commit()

    response = CardResponseModel(
        id=card.id,
        account_id=card.account_id,
        card_type=card.card_type,
        last_four=card.last_four,
        card_holder_name=card.card_holder_name,
        expiration_date=card.expiration_date,
        brand=card.brand,
        status=card.status,
    )

    return {"detail": "Card deleted successfully", "deleted_card": response}
