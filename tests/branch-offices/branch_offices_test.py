from src.constants.constants import ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT
from src.models.branch_offices import BranchOffice


def test_get_branch_offices_empty(client):
    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    assert response.json() == []


def test_get_one_branch_office(client, session, fake):
    branch_office = BranchOffice(
        name=fake.company(), address=fake.address(), contact=fake.phone_number()
    )

    session.add(branch_office)
    session.commit()

    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == branch_office.id
    assert data[0]["name"] == branch_office.name
    assert data[0]["address"] == branch_office.address
    assert data[0]["contact"] == branch_office.contact


def test_get_multiple_branch_offices(client, session, fake):
    branch_offices = []
    for _ in range(5):
        branch_office = BranchOffice(
            name=fake.company(), address=fake.address(), contact=fake.phone_number()
        )
        branch_offices.append(branch_office)
        session.add(branch_office)

    session.commit()

    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    for i in range(5):
        assert data[i]["id"] == branch_offices[i].id
        assert data[i]["name"] == branch_offices[i].name
        assert data[i]["address"] == branch_offices[i].address
        assert data[i]["contact"] == branch_offices[i].contact


def test_branch_offices_response_structure(client, session, fake):
    branch_office = BranchOffice(
        name=fake.company(), address=fake.address(), contact=fake.phone_number()
    )

    session.add(branch_office)
    session.commit()

    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1

    branch_office_data = data[0]
    assert "id" in branch_office_data
    assert "name" in branch_office_data
    assert "address" in branch_office_data
    assert "contact" in branch_office_data


def test_create_branch_office(client, session, fake):
    response = client.post(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "name" in data
    assert "address" in data
    assert "contact" in data

    branch_office_in_db = session.get(BranchOffice, data["id"])
    assert branch_office_in_db is not None
    assert branch_office_in_db.name == data["name"]
    assert branch_office_in_db.address == data["address"]
    assert branch_office_in_db.contact == data["contact"]


def test_delete_branch_office(client, session, fake):
    branch_office = BranchOffice(
        name=fake.company(), address=fake.address(), contact=fake.phone_number()
    )

    session.add(branch_office)
    session.commit()

    response = client.delete(
        f"{ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT}/{branch_office.id}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Branch office deleted successfully"
    assert "deleted_branch_office" in data
    assert data["deleted_branch_office"]["id"] == branch_office.id

    branch_office_in_db = session.get(BranchOffice, branch_office.id)
    assert branch_office_in_db is None


def test_delete_nonexistent_branch_office(client):
    response = client.delete(f"{ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT}/9999")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Branch office not found"
