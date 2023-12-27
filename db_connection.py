from config import config
from ibmcloudant import CouchDbSessionAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1


def get_db_connection():
    authenticator = CouchDbSessionAuthenticator(config['DBUSER'], config['DBPASS'])
    service = CloudantV1(authenticator=authenticator)
    service.set_service_url(config['COUCHDB'])
    return service
