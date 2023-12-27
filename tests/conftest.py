import pytest
from config import config
from db_connection import get_db_connection


@pytest.fixture()
def setup_db():
    config['DBNAME'] = 'jai-alai-kinielak-tests'
    yield
    conn = get_db_connection()
    all_docs = conn.post_all_docs(config['DBNAME']).get_result()
    for doc in all_docs['rows']:
        conn.delete_document(
            config['DBNAME'],
            doc['id'],
            rev=doc['value']['rev']
        )


@pytest.fixture()
def match_item():
    match = {
        "id": "2023-udazken-1",
        "name": "1. jardunaldia ",
        "description": "",
        "date": "2023-11-06T18:00:00",
        "tournament_id": "2023-udazken",
        "players": 6,
        "result": [0, 0, 0, 0, 0, 0]
    }
    return match


@pytest.fixture()
def tournament_item():
    tournament = {
        "id": "2023-udazken",
        "name": "Udazken torneoa",
        "description": "",
        "start_date": "2023-11-06T18:00:00",
    }
    return tournament


@pytest.fixture()
def create_match_item(setup_db, tournament_item, match_item):
    from db_connection import get_db_connection
    from ibmcloudant.cloudant_v1 import Document
    from config import config
    conn = get_db_connection()
    tournament = tournament_item.copy()
    tournament['type'] = "tournament"
    tournament['_id'] = tournament_item['id']
    tournament['date'] = tournament_item['start_date']
    doc = Document(**tournament)
    conn.put_document(db=config['DBNAME'], doc_id=tournament['_id'], document=doc)

    match = match_item.copy()
    match['type'] = 'match'
    match['_id'] = match_item['id']

    doc = Document(**match)
    conn.put_document(db=config['DBNAME'], doc_id=match['_id'], document=doc)
