from data_models import core
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
            if len(labels) > 0:
                self.properties["has_labels"] = True
                self.properties["labels"] = labels
                if "Member of Parliament" in labels:
                    self.get_mp_properties(self.n.vertex)
            return self.properties
        else:
            return None

    def get_mp_properties(self, node):
        self.properties["party"] = node["party"]


