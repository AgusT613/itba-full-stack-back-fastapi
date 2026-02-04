from src.constants.constants import ITBANK_ACCOUNTS_COMPLETE_ENDPOINT


def test_get_my_accounts_no_accounts(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(ITBANK_ACCOUNTS_COMPLETE_ENDPOINT)

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_account_details_not_found(client_auth):
    auth_client, _ = client_auth()

    response = auth_client.get(f"{ITBANK_ACCOUNTS_COMPLETE_ENDPOINT}/999999999")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Account not found"
