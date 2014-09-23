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
        print node["vote_number"], node["date"]
        for vote in node["votes"]:
            self._print_out(vote["full_name"], vote["vote"])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)