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

    def _set_properties(self):
        if self.n.exists:
            self.name = self.n.vertex["noun_phrase"]
            self._get_node_properties()
            node_labels = self.n.vertex.get_labels()
            self.labels = [l for l in node_labels if l not in self.exclude]
            if "Member of Parliament" in self.labels:
                self.get_mp_properties(self.n.vertex)

    def labels(self):
        for label in self.labels:
            yield label

    def is_mentioned_in(self):
        if "document_count" in self._properties:
            for doc in self._properties["documents"]:
                yield doc

    def is_associated_with(self):
        if "document_count" in self._properties:
            for doc in self._properties["documents"]:
                yield doc

    def _get_node_properties(self):
        stats = [x for x in self.n.get_stats()]
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
                x['title'] for x in self.n.get_documents()
            ]

        print "documents:"
        docs = [{"title": x['title']} for x in self.n.get_documents()]
        print docs
        print "outgoing:"
        out = [(x[0], self.get_node_name(x[1])) for x in self.n.get_outgoing()]
        print out
        self.get_node_name(out[0][1])
        print "incoming:"
        incoming = [(x[0], self.get_node_name(x[1])) for x in self.n.get_incoming()]
        print incoming

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


