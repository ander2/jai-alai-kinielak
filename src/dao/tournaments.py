import logging

from db_connection import get_db_connection
from config import config
from ibmcloudant.cloudant_v1 import Document


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jai')


def prepare_document(tournament: dict) -> dict:
    document = tournament.copy()
    document['_id'] = tournament['id']
    document['date'] = tournament['start_date']
    del document['id']
    del document['start_date']
    return document


def prepare_result(tournament: dict) -> dict:
    tournament['id'] = tournament['_id']
    tournament['start_date'] = tournament['date']
    del tournament['_id']
    del tournament['_rev']
    del tournament['date']
    return tournament


def get_item_from_db(item_id: str):
    try:
        conn = get_db_connection()
        tournament = conn.get_document(config['DBNAME'], item_id).get_result()
        return prepare_result(tournament)
    except Exception:
        raise RuntimeError('Item not found')


def get_items_from_db():
    all_tournaments = []
    try:
        conn = get_db_connection()
        tournaments = conn.post_all_docs(config['DBNAME'], include_docs=True).get_result()
        for tournament in tournaments['rows']:
            tournament = prepare_result(tournament['doc'])
            all_tournaments.append(tournament)
        return all_tournaments
    except Exception:
        raise RuntimeError('Item not found')


def create_tournament(tournament):
    try:
        conn = get_db_connection()
        t = prepare_document(tournament)
        doc = Document(**t)
        conn.put_document(config['DBNAME'], t['_id'], doc)
        return tournament
    except Exception as e:
        logger.error(e)
        raise RuntimeError('Cannot create item')


def update_tournament(id: str, tournament: dict) -> dict:
    try:
        conn = get_db_connection()
        h = conn.head_document(config['DBNAME'], id)
        rev = h.get_headers()['ETag'][1:-1]
        logger.error(h.get_headers())
        t = prepare_document(tournament)
        logger.error(t['_id'])
        doc = Document(**t)
        response = conn.put_document(
            db=config['DBNAME'],
            doc_id=t['_id'],
            document=doc,
            rev=rev
        ).get_result()
        if response['ok']:
            return tournament
        else:
            raise RuntimeError(f"{response['error']} {response['reason']}")
    except KeyError as e:
        logger.error(e, exc_info=True)
        raise RuntimeError('Item not found')
    except Exception as e:
        logger.error(e)
        raise RuntimeError('Cannot create item')
