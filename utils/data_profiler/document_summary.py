from utils.data_profiler import DataProfiler


class DocumentsSummary(DataProfiler):
    def __init__(self, verbose):
        DataProfiler.__init__(self)
        self.verbose = verbose
        self.all_features = []
        self.doc_types = [
            "Document",
            "Argument",
            "Act of Parliament",
            "Policy Category",
            "Policy Agenda"
        ]
        print "\n[**] Document Node Summary\n"

    def get_document_stats(self):
        print "Iterating All Documents..."
        if not self.verbose:
            self._print_count("type", "sent", "names", "terms", "rel", "")
        else:
            self._print_count("count", "sent", "names", "terms", "rel", "title")
        for type in self.doc_types:
            documents = [x for x in self.core_model.get_all_nodes(type)]
            self._itterate_documents(type, documents)
            print "---"
        self.export(self.all_features)

    def _itterate_documents(self, doc_type, documents):
        these_features = []
        for d in documents:
        #for d in test_documents[:10]:
            document = self.data_models.Document(d["link"])
            document.fetch()
            # rels = [s for s in document.get_feat_relationships()]
            sent_count = len([s for s in document.get_sentences()])
            names_count = len(
                [s for s in document.get_doc_features("Named Entity")]
            )
            terms_count = len(
                [s for s in document.get_doc_features("Unique Term")]
            )
            rel_count = names_count*terms_count
            features = {
                "sent_count": sent_count,
                "names_count": names_count,
                "terms_count": terms_count,
                "rel_count": rel_count,
                "title": d["title"]
            }
            these_features.append(features)
            self.all_features.append(features)
            total = len(these_features)
            if self.verbose:
                title = "%s - %s" % (doc_type, d["title"])
                self._print_count(
                    total,
                    sent_count,
                    names_count,
                    terms_count,
                    rel_count,
                    title
                )
        self.show_document_stats(doc_type, these_features)

    def show_document_stats(self, doc_type, features):
        document_count = len(features)
        sent_total = sum(item['sent_count'] for item in features)
        names_total = sum(item['names_count'] for item in features)
        terms_total = sum(item['terms_count'] for item in features)
        rel_total = sum(item['rel_count'] for item in features)
        self._print_count(
            doc_type,
            sent_total,
            names_total,
            terms_total,
            rel_total,
            "TOTALS"
        )
        self._print_count(
            doc_type,
            sent_total/document_count,
            names_total/document_count,
            terms_total/document_count,
            rel_total/document_count,
            "MEANS"
        )

    def export(self, data):
        file = "documents_export.csv"
        key = ["sent_count", "names_count", "terms_count", "rel_count", "title"]
        self.csv_handler.export_to_csv(file, key, data)

    def _print_count(self, doc_type, sent, names, terms, rel, category):
        output = " %-25s%-8s%-8s%-8s%-8s%-25s" % \
                 (doc_type, sent, names, terms, rel, category)
        print output