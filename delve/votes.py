from delve import ImportInterface


class ImportVotes(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Votes()

    def delve(self):
        for doc in self.cache.collection.find().batch_size(60):
            self._import(doc)

    def _import(self, node):
        print node["bill"]
        print node["vote_number"], node["date"]
        new_vote = self.data_models.VoteinParliament(
            node["vote_number"],
            node["bill"]
        )
        new_vote.create()
        new_vote.make_vote(node["date"])
        for vote in node["votes"]:
            vote_category = self.data_models.VoteCategory(node["bill"], vote["vote"])
            if not vote_category.exists:
                vote_category.create()
                vote_category.make_category()
            mp = self.data_models.MemberOfParliament(vote["full_name"])
            if mp.exists:
                vote_category.link_vote(mp)
            self._print_out(vote["full_name"], vote["vote"])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)