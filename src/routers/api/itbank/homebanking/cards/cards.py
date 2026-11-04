from fastapi import APIRouter, Depends, status
from src.models.cards import (
    CardCreate,
    CardPartialUpdate,
    CardFullUpdate,
)
from src.services.card_service import CardServiceDep
from src.utils.auth_user import CurrentUserDep, get_current_user

router = APIRouter(
    prefix="/cards", dependencies=[Depends(get_current_user)], tags=["cards"]
)


@router.get("/")
async def get_card_list(card_service: CardServiceDep, current_user: CurrentUserDep):
    return card_service.get_cards(current_user.id)


@router.get("/{card_id}")
async def get_card_details(
    card_id: int,
    card_service: CardServiceDep,
    current_user: CurrentUserDep,
):
    return card_service.get_card_details(card_id, current_user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_card(
    card: CardCreate,
    card_service: CardServiceDep,
    current_user: CurrentUserDep,
):
    return card_service.create_card(current_user.id, card)


@router.patch("/{card_id}")
async def update_card(
    card_id: int,
    card_update: CardPartialUpdate,
    card_service: CardServiceDep,
    current_user: CurrentUserDep,
):
    return card_service.update_card_partially(card_id, current_user.id, card_update)


@router.put("/{card_id}")
async def replace_card(
    card_id: int,
    card_update: CardFullUpdate,
    card_service: CardServiceDep,
    current_user: CurrentUserDep,
):
    return card_service.update_card_fully(card_id, current_user.id, card_update)


@router.delete("/{card_id}")
async def delete_card(
    card_id: int,
    card_service: CardServiceDep,
    current_user: CurrentUserDep,
):
    deleted_card = card_service.delete_card(card_id, current_user.id)
    return {"detail": "Card deleted successfully", "deleted_card": deleted_card}
