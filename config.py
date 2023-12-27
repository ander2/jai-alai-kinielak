import os

config = {
    'DBUSER': os.environ['dbuser'],
    'DBPASS': os.environ['dbpass'],
    'COUCHDB': os.environ['dburl'],
    'DBNAME': os.environ['dbname']
}
