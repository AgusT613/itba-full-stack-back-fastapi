from src.constants.constants import ITBANK_HOMEBANKING_COMPLETE_ENDPOINT


def test_get_homebanking_welcome_message(client_auth):
    auth_client, user = client_auth()

    response = auth_client.get(ITBANK_HOMEBANKING_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert "user" in data
    assert "itbank_account" in data
    assert "cards" in data
    assert "transfers" in data
    assert data["user"]["username"] == user.username


def test_get_homebanking_current_user_info(client_auth):
    auth_client, user = client_auth()

    response = auth_client.get(f"{ITBANK_HOMEBANKING_COMPLETE_ENDPOINT}/me")

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "full_name" in data
    assert "username" in data
    assert data["username"] == user.username
