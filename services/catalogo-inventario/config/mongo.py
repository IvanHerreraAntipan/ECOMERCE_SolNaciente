import os
from pymongo import MongoClient

_client = None

def get_mongo_client():
    global _client
    if _client is None:
        uri = os.getenv('MONGO_URI', 'mongodb://127.0.0.1:27017/?replicaSet=rs0')
        _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client

def get_db():
    client = get_mongo_client()
    db_name = os.getenv('MONGO_DB_NAME', 'ecommerce_catalogo')
    return client[db_name]