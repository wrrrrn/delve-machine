from interfaces import mongo


class Politicians:
    def __init__(self):
        self.mongo_interface = mongo.MongoInterface()
        self.collection = self.mongo_interface.db.politicians

    def write(self, document):
        return self.collection.insert(document)
