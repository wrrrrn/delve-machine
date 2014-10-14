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
            print "Existing Document"
            return None

    def get_document(self, key, value):
        result = self.collection.find({key: value}).limit(1)
        if result.count() > 0:
            return result[0]
        else:
            return None

    def fetch_all(self, return_list=False):
        if return_list:
            return list(self.collection.find())
        else:
            size = 60
            return self.collection.find().batch_size(size)

    def delete_data(self):
        self.collection.remove({})

    def create_index(self, key):
        try:
            self.collection.ensure_index(key, unique=True)
        except self.mongo_interface.index_error:
            print "Existing index"


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
        self.create_index('debate_id')

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


class Media(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.media
        self.create_index('link')


class PolicyAgenda(CacheModel):
    def __init__(self):
        CacheModel.__init__(self)
        self.collection = self.mongo_interface.db.policy

