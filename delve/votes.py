from delve import ImportInterface


class ImportVotes(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Votes()

    def delve(self):
        for doc in self.cache.collection.find():
            self._import(doc)

    def _import(self, node):
        print node["bill"]
        print node["date"]
        print node["vote_number"]