from data_profile import DataProfiler


class NounPhraseSummary(DataProfiler):
    def __init__(self, verbose):
        DataProfiler.__init__(self)
        self.verbose = verbose
        self.all_features = []
        print "\n[**] Noun Phrase Summary\n"
        self.np_types = [
            "Noun Phrase",
            "Member of Parliament",
            "Government Position",
            "Government Department",
            "Political Party"
        ]

    def get_np_stats(self):
        print "Iterating All Noun Phrases..."
        if not self.verbose:
            self._print_count(
                "sent", "ass", "docs", "", "type"
            )
        else:
            self._print_count(
                "sent", "ass", "docs", "noun phrase", ""
            )
        for type in self.np_types:
            all_noun_phrase = [x for x in self.core_model.get_all_nodes(type)]
            self._iterate_phrases(type, all_noun_phrase)
            print "---"
        self.export(self.all_features)

    def _iterate_phrases(self, np_type, all_noun_phrase):
        these_features = []
        for np in all_noun_phrase:
        #for np in test_phrase[:10]:
            name = np["noun_phrase"]
            n = self.data_models.NounPhrase(name)
            sentences = len([x for x in n.get_sentences()])
            documents = len([x for x in n.get_documents()])
            associated = len(
                [x for x in n.get_relationships("IS_ASSOCIATED_WITH")]
            )
            #associated_docs = len(
            #    [x for x in n.get_associated_documents()]
            #)
            features = {
                "associated": associated,
                "documents": documents,
                "sentences": sentences,
                "np": np["noun_phrase"]
            }
            total = "[%s]" % len(these_features)
            these_features.append(features)
            self.all_features.append(features)
            if self.verbose:
                self._print_count(
                    sentences, associated, documents, name, total
                )
        self.show_np_stats(np_type, these_features)

    def show_np_stats(self, np_type, features):
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
                np_type
            )
            self._print_count(
                sent_total/np_count,
                ass_total/np_count,
                doc_total/np_count,
                "MEANS",
                np_type
            )

    def export(self, data):
        file = "noun_phrase_export.csv"
        key = ["sentences", "associated", "documents", "np"]
        self.csv_handler.export_to_csv(file, key, data)

    def _print_count(self, sent, ass, docs, np, np_type):
        if self.verbose:
            output = " %-25s%-8s%-8s%-8s%-25s" % \
                     (np_type, sent, docs, ass, np)
        else:
            output = " %-25s%-8s%-8s%-8s%-20s" % \
                     (np_type, sent, docs, ass, np)
        print output