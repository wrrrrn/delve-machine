from data_profile import DataProfiler


class TermSummary(DataProfiler):
    def __init__(self, verbose):
        DataProfiler.__init__(self)
        self.verbose = verbose
        self.all_features = []
        print "\n[**] Term Summary\n"

    def get_term_stats(self):
        print "Iterating All Terms..."
        self._print_count("sent", "ass", "docs", "term", "")
        all_terms = [x["term"] for x in self.core_model.get_all_nodes("Unique Term")]
        self._iterate_terms(all_terms)
        self.export(self.all_features)
        self.show_term_stats(self.all_features)

    def _iterate_terms(self, terms):
        for unique in terms:
            #term = unique["term"]
            t = self.data_models.UniqueTerm(unique)
            sentences = len([x for x in t.get_sentences()])
            documents = len([x for x in t.get_documents()])
            print documents
            associated = len([x for x in t.get_relationships()])
            features = {
                "associated": associated,
                "documents": documents,
                "sentences": sentences,
                "term": unique
            }
            total = "[%s]" % len(self.all_features)
            self.all_features.append(features)
            if self.verbose:
                self._print_count(
                    sentences, associated, documents, unique, total
                )

    def show_term_stats(self, features):
        np_count = len(features)
        if np_count > 0:
            ass_total = sum(item['associated'] for item in features)
            doc_total = sum(item['documents'] for item in features)
            sent_total = sum(item['sentences'] for item in features)
            print "-"
            self._print_count(
                sent_total,
                ass_total,
                doc_total,
                "TOTAL",
                "Unique Terms"
            )
            self._print_count(
                sent_total/np_count,
                ass_total/np_count,
                doc_total/np_count,
                "MEANS",
                ""
            )

    def export(self, data):
        file = "term_export.csv"
        key = ["sentences", "associated", "documents", "term"]
        self.csv_handler.export_to_csv(file, key, data)

    def _print_count(self, sent, ass, docs, term, count):
        output = " %-25s%-8s%-8s%-8s%-25s" % \
                 (count, sent, docs, ass, term)
        print output