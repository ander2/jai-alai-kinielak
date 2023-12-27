import pytest
from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_post_score_point(create_match_item):
    score = {
        "player_id": 2
    }
    client.post("/matches/2023-udazken-1/scores", json=score)
    response = client.get("/matches/2023-udazken-1")
    response_match = response.json()
    print(response_match)
    assert response_match['result'][2] == 1


def test_put_score_point(create_match_item):
    score = {
        "player_id": 2,
        "points": 5
    }
    response = client.put("/matches/2023-udazken-1/scores", json=score)
    assert response.status_code == 200
    response = client.get("/matches/2023-udazken-1")
    response_match = response.json()
    print(response_match)
    assert response_match['result'][0] == 0
    assert response_match['result'][1] == 0
    assert response_match['result'][2] == 5
