import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_matches_list(setup_db, create_match_item, match_item):
    response = client.get("/matches")
    assert response.status_code == 200
    matches = response.json()
    assert len(matches) == 1
    assert matches == [match_item]


def test_matchs_get_item(setup_db, create_match_item, match_item):
    response = client.get("/matches/2023-udazken-1")
    assert response.status_code == 200
    assert response.json() == match_item


def test_create_match(setup_db, create_match_item):
    match = {
        "id": "2023-udazken-2",
        "name": "2. Jardunaldia",
        "description": "",
        "date": "2023-11-25T12:00:00",
        "tournament_id": "2023-udazken"
    }
    response = client.post("/matches", json=match)
    assert response.status_code == 201
    matches = client.get("/matches").json()
    assert len(matches) == 2
