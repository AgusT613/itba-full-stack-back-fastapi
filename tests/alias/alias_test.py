def test_get_aliases(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/alias/all")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    for alias in data:
        assert "alias" in alias


def test_get_itbank_aliases(client_auth):
    client, _ = client_auth()
    response = client.get("/api/homebanking/alias/itbank")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, object)
    assert "alias" in data
