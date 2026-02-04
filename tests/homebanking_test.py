from src.constants.constants import ITBANK_HOMEBANKING_COMPLETE_ENDPOINT


def test_get_homebanking_welcome_message(client_auth):
    auth_client, user = client_auth()

    response = auth_client.get(ITBANK_HOMEBANKING_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert (
        data["message"]
        == f"Welcome to ITBANK Homebanking {user.username.capitalize()}!"
    )
