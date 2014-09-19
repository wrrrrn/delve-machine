from interfaces import mongo


class CacheModel:
    def __init__(self):
        self.mongo_interface = mongo.MongoInterface()
        self.collection = None

    def write(self, document):
        try:
            result = self.collection.insert(document)
            return result
        except self.mongo_interface.duplicate_error:
            print "Existing Debate"
            return None

    def get_document(self, key, value):
        result = self.collection.find({key: value}).limit(1)
        if result.count() > 0:
            return result[0]
        else:
            return None


class Proto(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.test


class Politicians(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.politicians


class Votes(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.votes


class Legislation(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.legislation


class Debates(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.debates

    def add_subdocument(self, document_id, subdocument):
        result = self.collection.find(
            {"sub_topics.debate_id": subdocument["debate_id"]}
        )
        if result.count() == 0:
            return self.collection.update(
                {"debate_id": document_id},
                {"$addToSet": {"sub_topics": subdocument}}
            )
        else:
            print "Existing Sub"
            return None