from pymongo import MongoClient


class MongoInterface:
    def __init__(self):
        self.client = MongoClient()
        self.db = self.client.delve
        self.collection = None
        self.test()

    def test(self):
        print self.db.collection_names()

    def get_representatives(self):
        self.collection = self.db.representatives