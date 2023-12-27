import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


@pytest.fixture()
def tournament_item():
    tournament = {
        "id": "2023-udazken",
        "name": "Udazken torneoa",
        "description": "",
        "year": 2023,
        "start_date": "2023-11-06T18:00:00"
    }
    return tournament


@pytest.fixture()
def create_tournament_item(setup_db, tournament_item):
    from db_connection import get_db_connection
    from ibmcloudant.cloudant_v1 import Document
    from config import config
    # from src.dao import tournaments
    conn = get_db_connection()
    tournament = tournament_item.copy()
    tournament['type'] = 'tournament'
    tournament['_id'] = tournament_item['id']
    tournament['date'] = tournament_item['start_date']
    doc = Document(**tournament)
    conn.put_document(db=config['DBNAME'], doc_id=tournament['_id'], document=doc)


def test_read_main(setup_db):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "ok"}


def test_tournaments_list(setup_db, create_tournament_item, tournament_item):
    response = client.get("/tournaments")
    assert response.status_code == 200
    tournaments = response.json()
    assert len(tournaments) == 1
    assert tournaments == [tournament_item]


def test_tournaments_get_item(setup_db, create_tournament_item, tournament_item):
    response = client.get("/tournaments/2023-udazken")
    assert response.status_code == 200
    assert response.json() == tournament_item


def test_tournaments_get_item_bad_identifier():
    response = client.get("/tournaments/2023")
    assert response.status_code == 404
    assert response.json()["detail"].find("not found") > -1


def test_create_tournament(setup_db):
    tournament = {
        "id": "2023-udaberri",
        "name": "Udaberri torneoa",
        "description": "",
        "year": 2024,
        "start_date": "2024-03-25T12:00:00"
    }
    response = client.post("/tournaments", json=tournament)
    assert response.status_code == 201


@pytest.mark.parametrize('missing_property',
                         ['name', 'description', 'start_date', 'year'])
def test_create_tournament_with_invalid_data(setup_db, missing_property, tournament_item):
    tournament = tournament_item.copy()
    del tournament[missing_property]
    response = client.post("/tournaments", json=tournament)
    assert response.status_code == 422


def test_modify_tournament(setup_db, create_tournament_item, tournament_item):
    tournament_item['name'] = 'Udazken-Negu txapelketa'
    response = client.put("/tournaments/2023-udazken", json=tournament_item)
    assert response.status_code == 200
    assert response.json() == tournament_item
