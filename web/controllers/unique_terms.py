from data_models import models


class UniqueTermsController:
    def __init__(self, term=False):
        self.term = term
        self.t = models.UniqueTerm(self.term)
        self.t.fetch()
        self.exists = self.t.exists
        self.has_associated = False
        self._properties = {}
        self._set_properties()

    def mentions_in_media(self):
        for doc, labels in self._properties["documents"]:
            if 'Public Media' in labels:
                yield {
                    "publication": doc["publication"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "summary": doc["summary"],
                    "link": doc["link"],
                    "sentiment": doc["sentiment_mean"],
                    "subjectivity": doc["subjectivity_mean"]
                }

    def mentions_in_debate(self):
        for doc, labels in self._properties["documents"]:
            if 'Debate Argument' in labels or 'Argument' in labels:
                yield {
                    "publication": doc["publication"],
                    "title": doc["title"],
                    "content": doc["content"],
                    "link": doc["link"],
                    "sentiment": doc["sentiment_mean"],
                    "subjectivity": doc["subjectivity_mean"]
                }

    def associated(self):
        for node, count in self._properties["associated"]:
            details = self._get_node_name(node)
            yield {
                "edge": details[0],
                "type": details[1],
                "count": count
            }

    def _set_properties(self):
        if self.t.exists:
            self._get_node_properties()
            self.term = self._properties["term"]
            self._set_documents()

    def _get_node_properties(self):
        stats = [x for x in self.t.get_stats()]
        self._properties["term"] = self.t.vertex["term"]
        self._properties["sentence_count"] = stats[0]
        self._properties["document_count"] = stats[1]
        self._properties["associated"] = [l for l in self.t.get_associated()]
        if len(self._properties["associated"]) > 0:
            self.has_associated = True

    def _set_documents(self):
        if self._properties["document_count"] > 0:
            self._has_mentioned_in = True
            documents = [(d, list(d.get_labels())) for d in self.t.get_documents()]
            doc_labels = [doc[1] for doc in documents]
            self._properties["documents"] = documents
            for labels in doc_labels:
                if 'Public Media' in labels:
                    self.has_mentions_in_media = True
                if 'Debate Argument' in labels or 'Argument' in labels:
                    self.has_mentions_in_debate = True
        else:
            self._properties["documents"] = []

    def _get_terms(self):
        return [t for t in self.n.get_terms_in_parliament()]

    def _get_node_name(self, node):
        #print node
        if "noun_phrase" in node:
            return node["noun_phrase"], "name"
        if "term" in node:
            return node["term"], "term"
        elif "sentence" in node:
            return node["sentence"], "sentence"
        elif "title" in node:
            return node["title"], "document"

    def show_properties(self):
        for prop in self._properties:
            if prop in ["outgoing", "incoming"]:
                print "*", prop
                for rel in self._properties[prop]:
                    self._print_out(rel, " ")
            else:
                self._print_out(prop, self._properties[prop])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)

