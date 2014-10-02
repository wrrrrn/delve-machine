from data_models import models


class NamedEntityController:
    def __init__(self, name=False):
        self.noun_phrase = name
        self.n = models.NounPhrase(self.noun_phrase)
        self.n.fetch()
        self.exists = self.n.exists
        self.node_type = "NamedEntity"
        self.exclude = ['Named Entity', 'Noun Phrase']
        self.name = ""
        self._properties = {}
        self.outgoing = []
        self.incoming = []
        self._is_mp = False
        self._has_stated = False
        self._has_associated_with = False
        self._has_mentioned_in = False
        self._has_member_of = False
        self._has_in_position = False
        self._set_properties()

    def labels(self):
        for label in self.labels:
            yield label

    def is_mentioned_in(self):
        for doc in self._properties["documents"]:
            yield doc

    def is_associated_with(self):
        for rel in self._properties["outgoing"]:
            if rel[0] == "IS_ASSOCIATED_WITH":
                yield {"type": rel[1][0], "edge": rel[1][1]}
        yield None

    def stated(self):
        for rel in self._properties["outgoing"]:
            if rel[0] == "STATED":
                yield {"edge": rel[1]}

    def member_of(self):
        for rel in self._properties["outgoing"]:
            if rel[0] == "MEMBER_OF":
                yield {"edge": rel[1]}

    def in_position(self):
        for rel in self._properties["outgoing"]:
            if rel[0] == "IN_POSITION":
                self._has_in_position = True
                yield {"edge": rel[1]}

    def show_properties(self):
        for prop in self._properties:
            if prop in ["outgoing", "incoming"]:
                print "*", prop
                for rel in self._properties[prop]:
                    self._print_out(rel, " ")
            else:
                self._print_out(prop, self._properties[prop])

    def _set_properties(self):
        if self.n.exists:
            self._get_node_properties()
            self.name = self._properties["name"]
            self.labels = self._properties["labels"]

    def _get_node_properties(self):
        stats = [x for x in self.n.get_stats()]
        self._properties["name"] = self.n.vertex["noun_phrase"]
        self._properties["labels"] = [
            l for l in self.n.vertex.get_labels() if l not in self.exclude
        ]
        self._properties["sentence_count"] = stats[0]
        self._properties["document_count"] = stats[1]
        self._properties["term_count"] = stats[2]
        self._set_document_properties()
        self._set_outgoing_properties()
        self._set_incoming_properties()
        self._set_document_properties()

    def _set_mp_properties(self, node):
        if "Member of Parliament" in self._properties["labels"]:
            self._is_mp = True
            self._set_mp_properties(self.n.vertex)
            self._properties["party"] = node["party"]
            self._properties["terms_in_parliament"] = node["number_of_terms"]
            self._properties["guardian_url"] = node["guardian_url"]
            self._properties["publicwhip_url"] = node["publicwhip_url"]

    def _set_document_properties(self):
        if self._properties["document_count"] > 0:
            self._has_mentioned_in = True
            self._properties["documents"] = [
                {"title": x['title']} for x in self.n.get_documents()
            ]
        else:
            self._properties["documents"] = []

    def _set_outgoing_properties(self):
        self._properties["outgoing"] = [
            (x[0], self._get_node_name(x[1])) for x in self.n.get_outgoing()
        ]
        for rel in self._properties["outgoing"]:
            if rel[0] == "IS_ASSOCIATED_WITH":
                self._has_associated_with = True
            elif rel[0] == "STATED":
                self._has_stated = True
            elif rel[0] == "MEMBER_OF":
                self._has_member_of = True
            elif rel[0] == "IN_POSITION":
                self._has_in_position = True

    def _set_incoming_properties(self):
        self._properties["incoming"] = [
            (x[0], self._get_node_name(x[1])) for x in self.n.get_incoming()
        ]

    def _get_node_name(self, node):
        #print node
        if "noun_phrase" in node:
            return node["noun_phrase"]
        if "term" in node:
            return "term", node["term"]
        elif "sentence" in node:
            return node["sentence"]
        elif "title" in node:
            return node["title"]


    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)

