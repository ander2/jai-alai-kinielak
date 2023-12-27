import logging

from db_connection import get_db_connection
from config import config
from ibmcloudant.cloudant_v1 import Document


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('jai')


def prepare_document(match: dict) -> dict:
    document = match.copy()
    document['_id'] = match['id']
    del document['id']
    if 'type' not in document:
        document['type'] = 'match'
    return document


def prepare_result(match: dict) -> dict:
    match['id'] = match['_id']
    del match['_id']
    del match['_rev']
    del match['type']
    return match


def get_item_from_db(item_id: str):
    try:
        conn = get_db_connection()
        match = conn.get_document(config['DBNAME'], item_id).get_result()
        return prepare_result(match)
    except Exception:
        raise RuntimeError('Item not found')


def get_items_from_db():
    all_matches = []
    try:
        conn = get_db_connection()
        matches = conn.post_all_docs(config['DBNAME'], include_docs=True).get_result()
        for match in matches['rows']:
            if match['doc'].get('type', '') == 'match':
                match = prepare_result(match['doc'])
                all_matches.append(match)
        return all_matches
    except Exception:
        raise RuntimeError('Item not found')


def create_match(match: dict):
    try:
        conn = get_db_connection()
        match['result'] = [0] * match['players']
        t = prepare_document(match)
        doc = Document(**t)
        conn.put_document(config['DBNAME'], t['_id'], doc)
        return match
    except Exception as e:
        logger.error(e)
        raise RuntimeError('Cannot create item')


def update_match(id: str, match: dict) -> dict:
    try:
        conn = get_db_connection()
        h = conn.head_document(config['DBNAME'], id)
        rev = h.get_headers()['ETag'][1:-1]
        logger.error(h.get_headers())
        t = prepare_document(match)
        logger.error(t['_id'])
        doc = Document(**t)
        response = conn.put_document(
            db=config['DBNAME'],
            doc_id=t['_id'],
            document=doc,
            rev=rev
        ).get_result()
        if response['ok']:
            return match
        else:
            raise RuntimeError(f"{response['error']} {response['reason']}")
    except KeyError as e:
        logger.error(e, exc_info=True)
        raise RuntimeError('Item not found')
    except Exception as e:
        logger.error(e)
        raise RuntimeError('Cannot create item')


def score_point(id: str, score: dict) -> bool:
    try:
        match = get_item_from_db(id)
    except Exception:
        raise RuntimeError('Match not found')

    try:
        match['result'][score['player_id']] += 1
        update_match(id, match)
    except KeyError as e:
        logger.error(e)
        raise RuntimeError('Player not found')


def update_score(id: str, score: dict) -> dict:
    try:
        conn = get_db_connection()
        doc = conn.get_document(config['DBNAME'], id).get_result()
        # doc = Document(**t)
        doc['result'][score['player_id']] = score['points']
        response = conn.put_document(
            db=config['DBNAME'],
            doc_id=id,
            document=doc
        ).get_result()
        if response['ok']:
            return doc
        else:
            raise RuntimeError(f"{response['error']} {response['reason']}")
    except KeyError as e:
        logger.error(e, exc_info=True)
        raise RuntimeError('Item not found')
    except Exception as e:
        logger.error(e)
        raise RuntimeError('Cannot create item')
