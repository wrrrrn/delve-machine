from data_models import models


class NamedEntityController:
    def __init__(self, name=False):
        self.noun_phrase = name
        self.n = models.NounPhrase(self.noun_phrase)
        self.n.fetch()
        self.exists = self.n.exists
        self.exclude = ['Named Entity', 'Noun Phrase']
        self.properties = {}

    def get_properties(self):
        if self.n.exists:
            node_labels = self.n.vertex.get_labels()
            labels = [l for l in node_labels if l not in self.exclude]
            self.properties["node_type"] = "NamedEntity"
            self.properties["name"] = self.n.vertex["noun_phrase"]
            self.get_node_properties()
            if len(labels) > 0:
                self.properties["has_labels"] = True
                self.properties["labels"] = labels
                if "Member of Parliament" in labels:
                    self.get_mp_properties(self.n.vertex)
            return self.properties
        else:
            return None

    def is_mentioned_in(self):
        if "document_count" in self.properties:
            for doc in self.properties["documents"]:
                yield doc

    def is_associated_with(self):
        if "document_count" in self.properties:
            for doc in self.properties["documents"]:
                yield doc


    def get_node_properties(self):
        stats = [x for x in self.n.get_stats()]
        self.properties["sentence_count"] = stats[0]
        self.properties["document_count"] = stats[1]
        self.properties["term_count"] = stats[2]
        self.properties["outgoing"] = [
            (x[0], self.get_node_name(x[1])) for x in self.n.get_outgoing()
        ]
        self.properties["incoming"] = [
            (x[0], self.get_node_name(x[1])) for x in self.n.get_incoming()
        ]
        if self.properties["document_count"] > 0:
            self.properties["documents"] = [
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
        self.properties["party"] = node["party"]
        self.properties["terms_in_parliament"] = node["number_of_terms"]
        self.properties["guardian_url"] = node["guardian_url"]
        self.properties["publicwhip_url"] = node["publicwhip_url"]

    def get_node_name(self, node):
        if "term" in node:
            return node["term"]
        elif "sentence" in node:
            return node["sentence"]
        elif "title" in node:
            return node["title"]


