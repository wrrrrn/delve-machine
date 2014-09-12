from interfaces import mongo


class Representatives:
    def __init__(self):
        self.mongo_interface = mongo.MongoInterface()
        self.collection = self.mongo_interface.db.representatives

    def write(self, document):
        return self.collection.insert(document)
