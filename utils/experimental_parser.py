

class ExperimentalParser:
    def __init__(self, speech_tools):
        self.speech_tools = speech_tools
        self.text_tools = self.speech_tools.TextHandler()
        self.tfidf_model = self.speech_tools.TfidfModel()
        self.tfidf_model.load()
        self._reset_counters()
        self._semantic_feats = []

    def parse_document(self, document):
        bag_of_words = self.text_tools.get_words(
            document,
            with_punctuation=False,
            remove_stopwords=True
        )
        self._words_total = len(bag_of_words)
        self._get_terms(bag_of_words)
        sentences = self.text_tools.get_sentences(document)
        for sentence_number, s in enumerate(sentences):
            print "PARSING:", s
            self._map_features(s)
        self._get_semantic_stats()

    def _map_features(self, text):
        names, names2, terms, senti, subj = self._get_semantic_features(text)


    def _get_semantic_features(self, sentence):
        words = self.text_tools.get_words(sentence)
        text_blob = self.text_tools.text_blob(sentence)
        names = self.text_tools.get_all_entities(sentence)
        #names2 = self.text_tools.get_all_entities(sentence)
        names2 = self.text_tools.get_all_entities_blob(sentence)
        # noun_phrases = text_blob.noun_phrases
        sentiment = text_blob.sentiment.polarity
        subjectivity = text_blob.sentiment.subjectivity
        terms = self.speech_tools.unique_list(
            [w for w in words if w in self.document_terms]
        )
        if len(names) > 0:
            self._all_names.extend(names)
        if len(terms) > 0:
            self._all_terms.extend(terms)
        self._all_sentiment.extend([sentiment])
        self._all_subjectivity.extend([subjectivity])
        self._print_semantics(names, names2, terms, sentiment, subjectivity)
        return names, names2, terms, sentiment, subjectivity

    def _get_terms(self, words):
        tfidf_results = self.tfidf_model.classify(words, score=False)
        self.document_terms = tfidf_results

    def _get_semantic_stats(self):
        pos_sentiment = [x for x in self._all_sentiment if x > 0]
        neg_sentiment = [x for x in self._all_sentiment if x < 0]
        named_entity_unique = len(
            self.text_tools.unique_lemmas(self._all_names)
        )
        self._semantic_feats = {
            "words_total": self._words_total,
            "named_entity_count": named_entity_unique,
            "unique_term_count": len(self._all_terms),
            "pos_sentiments": len(pos_sentiment),
            "neg_sentiments": len(neg_sentiment)
        }
        if len(self._all_sentiment) > 0:
            self._semantic_feats["sentiment_mean"] = \
            sum(self._all_sentiment)/len(self._all_sentiment)
        if len(self._all_subjectivity) > 0:
            self._semantic_feats["subjectivity_mean"] = \
                sum(self._all_subjectivity)/len(self._all_subjectivity)

        self._print_out()
        self._reset_counters()

    def _print_semantics(self, names, names2, terms, sentiment, subjectivity):
        print "\n** named entities", names
        print "** named entities", names2
        print "** unique terms", terms
        #print "** noun phrases", noun_phrases
        print "** sentiment", sentiment
        print "** subjectivity", subjectivity, '\n'

    def _print_out(self):
        print "\n---DOCUMENT SUMMARY---"
        for x in self._semantic_feats:
            print " %-30s%-25s%-20s" % (x, self._semantic_feats[x], "")
        print "---     SUMMARY   ---\n"

    def _reset_counters(self):
        self._words_total = ""
        self._all_statements = []
        self._all_names = []
        self._all_terms = []
        self._all_nounphrases = []
        self._all_relations = []
        self._all_sentiment = []
        self._all_subjectivity = []