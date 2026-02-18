from src.models.accounts import BankAccount
from src.models.cards import Card


def test_get_card_list_empty(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/cards")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_card_list_with_cards(client_auth, session, fake):
    client, user = client_auth()

    account = BankAccount(
        account_number=fake.bban(),
        account_type="checking",
        balance=1000.0,
        user_id=user.id,
        description=fake.text(max_nb_chars=200),
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
    assert response.status_code == 200
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
    assert response.status_code == 200
    cards = response.json()
    assert isinstance(cards, list)
    assert len(cards) == 2
    card_ids = {card["id"] for card in cards}
    assert card1.id in card_ids
    assert card2.id in card_ids
