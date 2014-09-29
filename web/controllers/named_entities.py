from data_models import models


class NamedEntityController:
    def __init__(self, name=False):
        self.noun_phrase = name
        self.exclude = ['Named Entity', 'Noun Phrase']
        self._properties = {}
        self.n = models.NounPhrase(self.noun_phrase)
        self.n.fetch()
        self.exists = self.n.exists
        self.node_type = "NamedEntity"
        self.name = ""
        self.outgoing = []
        self.incoming = []
        self._is_mp = False
        self._set_properties()

    def _set_properties(self):
        if self.n.exists:
            self._get_node_properties()
            self.name = self._properties["name"]
            self.labels = self._properties["labels"]

    def labels(self):
        for label in self.labels:
            yield label

    def is_mentioned_in(self):
        for doc in self._properties["documents"]:
            yield doc

    def is_associated_with(self):
        for rel in self._properties["outgoing"]:
            if rel[0] == "IS_ASSOCIATED_WITH":
                yield rel

    def _get_node_properties(self):
        stats = [x for x in self.n.get_stats()]
        self._properties["name"] = self.n.vertex["noun_phrase"]
        self._properties["labels"] = [
            l for l in self.n.vertex.get_labels() if l not in self.exclude
        ]
        self._properties["sentence_count"] = stats[0]
        self._properties["document_count"] = stats[1]
        self._properties["term_count"] = stats[2]
        self._properties["outgoing"] = [
            (x[0], self.get_node_name(x[1])) for x in self.n.get_outgoing()
        ]
        self._properties["incoming"] = [
            (x[0], self.get_node_name(x[1])) for x in self.n.get_incoming()
        ]
        if self._properties["document_count"] > 0:
            self._properties["documents"] = [
                {"title": x['title']} for x in self.n.get_documents()
            ]
        if "Member of Parliament" in self._properties["labels"]:
            self._is_mp = True
            self.get_mp_properties(self.n.vertex)

    def get_mp_properties(self, node):
        self._properties["party"] = node["party"]
        self._properties["terms_in_parliament"] = node["number_of_terms"]
        self._properties["guardian_url"] = node["guardian_url"]
        self._properties["publicwhip_url"] = node["publicwhip_url"]

    def get_node_name(self, node):
        if "term" in node:
            return node["term"]
        elif "sentence" in node:
            return node["sentence"]
        elif "title" in node:
            return node["title"]

    def show_properties(self):
        for prop in self._properties:
            self._print_out(prop, self._properties[prop])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)

