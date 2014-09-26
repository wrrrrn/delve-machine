from data_models import core
from data_models import models


class NamedEntityController:
    def __init__(self, name=False):
        self.noun_phrase = name
        self.n = models.NounPhrase(self.noun_phrase)
        self.n.fetch()
        self.properties = {}

    def get_properties(self):
        if self.n.exists:
            self.properties["node_type"] = "NamedEntity"
            self.properties["name"] = self.n.vertex["title"]
            self.properties["content"] = self.n.vertex["content"]
            self.properties["mentions"] = self.get_mentions()
            self.properties["domain"] = self.n.vertex["publication"]
            return self.properties
        else:
            return None

    def get_mentions(self):
        names = self.n.get_mentions("Named Entity")
        terms = self.n.get_mentions("Unique Term")
        n = [{"type": "name", "value": n["noun_phrase"]} for n in names]
        t = [{"type": "term", "value": t["term"]} for t in terms]
        for mention in n:
            yield mention

