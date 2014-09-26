from data_models import core
from data_models import models


class DocumentController:
    def __init__(self, link=False):
        self.link = link
        self.d = core.Document(self.link)
        self.d.fetch()
        self.exists = self.d.exists
        self.properties = {}

    def get_properties(self):
        self.properties["title"] = self.d.vertex["title"]
        self.properties["content"] = self.d.vertex["content"]
        self.properties["mentions"] = self.get_mentions()
        self.properties["domain"] = self.d.vertex["publication"]
        return self.properties

    def get_mentions(self):
        names = self.d.get_mentions("Named Entity")
        terms = self.d.get_mentions("Unique Term")
        n = [{"type": "name", "value": n["noun_phrase"]} for n in names]
        t = [{"type": "term", "value": t["term"]} for t in terms]
        for mention in n:
            yield mention


