from pymongo import MongoClient


class MongoInterface:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.delve
        self._collections()

    def _collections(self):
        print self.db.collection_names()


