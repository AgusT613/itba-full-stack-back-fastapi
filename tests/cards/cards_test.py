from src.models.accounts import BankAccount
from src.models.cards import Card
from fastapi import status


def test_get_card_list_empty(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/cards")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)


def test_get_card_list_with_cards(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    response = client.get("/api/homebanking/cards")
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()
    assert isinstance(cards, list)
    assert len(cards) == 1
    assert cards[0]["id"] == card.id


def test_get_card_list_with_multiple_cards(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card1 = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    card2 = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="credit",
        last_four="5678",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Mastercard",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add_all([card1, card2])
    session.commit()
    session.refresh(card1)
    session.refresh(card2)

    response = client.get("/api/homebanking/cards")
    assert response.status_code == status.HTTP_200_OK
    cards = response.json()
    assert isinstance(cards, list)
    assert len(cards) == 2
    card_ids = {card["id"] for card in cards}
    assert card1.id in card_ids
    assert card2.id in card_ids


def test_get_card_by_id(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    response = client.get(f"/api/homebanking/cards/{card.id}")
    assert response.status_code == status.HTTP_200_OK
    card_data = response.json()
    assert card_data["id"] == card.id
    assert card_data["account_id"] == account.id
    assert card_data["card_type"] == "debit"
    assert card_data["last_four"] == "1234"
    assert card_data["card_holder_name"] == card.card_holder_name
    assert card_data["expiration_date"].split("T")[0] == card.expiration_date.strftime(
        "%Y-%m-%d"
    )
    assert card_data["brand"] == "Visa"
    assert card_data["status"] == "active"


def test_get_card_by_id_not_found(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/cards/9999")  # Non-existent card ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Card not found"


def test_create_card(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card_data = {
        "account_id": account.id,
        "card_type": "debit",
        "last_four": "1234",
        "card_holder_name": fake.name(),
        "expiration_date": str(fake.future_date()),
        "brand": "Visa",
        "status": "active",
        "pin": fake.password(),
    }

    response = client.post("/api/homebanking/cards", json=card_data)
    assert response.status_code == status.HTTP_201_CREATED
    card = response.json()
    assert card["account_id"] == account.id
    assert card["card_type"] == "debit"
    assert card["last_four"] == "1234"
    assert card["card_holder_name"] == card_data["card_holder_name"]
    assert card["expiration_date"].split("T")[0] == card_data["expiration_date"]
    assert card["brand"] == "Visa"
    assert card["status"] == "active"


def test_create_card_invalid_account(client_auth, fake):
    client, _ = client_auth()

    card_data = {
        "account_id": 9999,  # Non-existent account ID
        "card_type": "debit",
        "last_four": "1234",
        "card_holder_name": fake.name(),
        "expiration_date": str(fake.future_date()),
        "brand": "Visa",
        "status": "active",
        "pin": fake.password(),
    }

    response = client.post("/api/homebanking/cards", json=card_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Invalid account ID"


def test_partial_update_card(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    update_data = {"status": "inactive"}

    response = client.patch(f"/api/homebanking/cards/{card.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_card = response.json()
    assert updated_card["id"] == card.id
    assert updated_card["status"] == "inactive"
    assert updated_card["card_type"] == "debit"  # Unchanged
    assert updated_card["last_four"] == "1234"  # Unchanged
    assert updated_card["card_holder_name"] == card.card_holder_name  # Unchanged
    assert updated_card["expiration_date"].split("T")[
        0
    ] == card.expiration_date.strftime(
        "%Y-%m-%d"
    )  # Unchanged
    assert updated_card["brand"] == "Visa"  # Unchanged


def test_partial_update_card_not_found(client_auth):
    client, _ = client_auth()
    update_data = {"status": "inactive"}
    response = client.patch(
        "/api/homebanking/cards/9999", json=update_data
    )  # Non-existent card ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Card not found"


def test_full_update_card(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    update_data = {
        "card_type": "credit",
        "card_holder_name": fake.name(),
        "expiration_date": str(fake.future_date()),
        "status": "inactive",
    }

    response = client.put(f"/api/homebanking/cards/{card.id}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    updated_card = response.json()
    assert updated_card["id"] == card.id
    assert updated_card["card_type"] == "credit"
    assert updated_card["card_holder_name"] == update_data["card_holder_name"]
    assert (
        updated_card["expiration_date"].split("T")[0] == update_data["expiration_date"]
    )
    assert updated_card["status"] == "inactive"


def test_full_update_card_not_found(client_auth, fake):
    client, _ = client_auth()
    update_data = {
        "card_type": "credit",
        "card_holder_name": fake.name(),
        "expiration_date": str(fake.future_date()),
        "status": "inactive",
    }
    response = client.put(
        "/api/homebanking/cards/9999", json=update_data
    )  # Non-existent card ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Card not found"


def test_full_update_card_missing_fields(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    update_data = {
        "card_type": "credit",
        # Missing card_holder_name and expiration_date
        "status": "inactive",
    }

    response = client.put(f"/api/homebanking/cards/{card.id}", json=update_data)
    assert (
        response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    )  # Unprocessable Entity due to missing fields


def test_delete_card(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
        alias=fake.unique.word(),
    )

    session.add(account)
    session.commit()
    session.refresh(account)

    card = Card(
        account_id=account.id,
        user_id=user.id,
        card_type="debit",
        last_four="1234",
        card_holder_name=fake.name(),
        expiration_date=fake.future_date(),
        brand="Visa",
        status="active",
        hashed_pin=fake.password(),
    )

    session.add(card)
    session.commit()
    session.refresh(card)

    response = client.delete(f"/api/homebanking/cards/{card.id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["detail"] == "Card deleted successfully"
    assert data["deleted_card"]["id"] == card.id
    assert data["deleted_card"]["card_type"] == "debit"
    assert data["deleted_card"]["last_four"] == "1234"
    assert data["deleted_card"]["status"] == "active"
    assert data["deleted_card"]["brand"] == "Visa"
    assert data["deleted_card"]["account_id"] == account.id


def test_delete_card_not_found(client_auth):
    client, _ = client_auth()
    response = client.delete("/api/homebanking/cards/9999")  # Non-existent card ID
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Card not found"
