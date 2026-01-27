from fastapi.testclient import TestClient
from src.constants.constants import ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT
from src.db.connection import SessionDep
from src.models.branch_offices import BranchOffice
from faker import Faker

fake = Faker()

def test_get_branch_offices_empty(client: TestClient):
    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    assert response.json() == []

def test_get_one_branch_office(client: TestClient, session: SessionDep):
    branch_office = BranchOffice(
        name=fake.company(),
        address=fake.address(),
        contact=fake.phone_number()
    )

    session.add(branch_office)
    session.commit()

    response = client.get(ITBANK_BRANCH_OFFICES_COMPLETE_ENDPOINT)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['id'] == branch_office.id
    assert data[0]['name'] == branch_office.name
    assert data[0]['address'] == branch_office.address
    assert data[0]['contact'] == branch_office.contact