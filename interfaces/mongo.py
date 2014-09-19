from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError


class MongoInterface:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.delve
        self._collections()
        self.duplicate_error = DuplicateKeyError

    def _collections(self):
        print self.db.collection_names()


