from data_models import core
from data_models import models


class DocumentController:
    def __init__(self, link=False):
        self.link = link
        self.d = core.Document(self.link)
        self.d.fetch()
        self.exists = self.d.exists
        self.title = None
        self.content = None
        self.publication = None
        self._properties = {}
        self._set_properties()

    def name_mentions(self):
        for mention in self._properties["name_mentions"]:
            if mention["type"] == "name":
                yield mention

    def topic_mentions(self):
        for mention in self._properties["term_mentions"]:
            if mention["type"] == "term":
                yield mention

    def _set_properties(self):
        if self.d.exists:
            self._get_node_properties()
            self.title = self._properties["title"]
            self.content = self._properties["content"]
            self.publication = self._properties["publication"]

    def _get_node_properties(self):
        self._properties["title"] = self.d.vertex["title"]
        self._properties["content"] = self._format(self.d.vertex["content"])
        self._properties["publication"] = self.d.vertex["publication"]
        self._set_mentions()

    def _set_mentions(self):
        get_names = self.d.get_doc_features("Named Entity")
        get_terms = self.d.get_doc_features("Unique Term")
        names = [
            {
                "type": "name",
                "value": n[0]["noun_phrase"],
                "count": n[1]
            } for n in get_names
        ]
        terms = [
            {
                "type": "term",
                "value": t[0]["term"],
                "count": t[1]
            } for t in get_terms
        ]
        self._properties["top_mentions"] = names[:3] + terms[:3]
        self._properties["name_mentions"] = names
        self._properties["term_mentions"] = terms
        print self._properties["top_mentions"]

    def _format(self, string):
        old_content = string.split("\n\n")
        new_content = ""
        for para in old_content:
            new_content += "<p>%s</p>" % para
        return new_content


