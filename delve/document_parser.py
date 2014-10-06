from utils import relation_extraction


class DocumentParser:
    def __init__(self, database, models, speech_tools):
        self.g = database
        self.relation_extractor = relation_extraction.Relations()
        self.core_model = models.DataModel()
        self.data_models = models
        self.speech_tools = speech_tools
        self.text_tools = self.speech_tools.TextHandler()
        self.tfidf_model = self.speech_tools.TfidfModel()
        self.tfidf_model.load()
        self._set_counters()
        self._semantic_feats = []

    def parse_document(self, document, content, map_statements=True):
        bag_of_words = self.text_tools.get_words(
            content,
            with_punctuation=False,
            remove_stopwords=True
        )
        self._words_total = len(bag_of_words)
        self._get_terms(bag_of_words)
        sentences = self.text_tools.get_sentences(content)
        for sentence_number, s in enumerate(sentences):
            print "PARSING:", s
            sentence_id = "%s::%s" % (document.vertex["link"], sentence_number)
            sentence = self._create_sentence_node(sentence_id, s)
            document.link_sentence(sentence.vertex)
            if sentence_number > 0:
                prev_sentence_id = "%s::%s" % (
                    document.vertex["link"], 
                    sentence_number-1
                )
                prev_sentence = self._create_sentence_node(prev_sentence_id, s)
                if prev_sentence.exists:
                    sentence.link_previous(prev_sentence)
            self._map_features(sentence, s)
        self._get_semantic_stats(document)

    def _create_sentence_node(self, sentence_id, sentence):
        sentence_node = self.data_models.Sentence(sentence_id)
        if not sentence_node.exists:
            sentence_node.create()
            sentence_node.vertex["sentence"] = sentence
        return sentence_node

    def _get_terms(self, words):
        tfidf_results = self.tfidf_model.classify(words, score=False)
        self.document_terms = tfidf_results

    def _map_features(self, sentence, text):
        names, terms, senti, subj = self._get_semantic_features(text)
        sentence.vertex["sentiment"] = senti
        sentence.vertex["subjectivity"] = subj
        for name in names:
            new_name = self.data_models.NounPhrase(name)
            if not new_name.exists:
                new_name.create()
            new_name.vertex.add_labels("Named Entity")
            new_name.link_sentence(sentence)
        for term in terms:
            new_term = self.data_models.UniqueTerm(term)
            if not new_term.exists:
                new_term.create()
            new_term.link_sentence(sentence)
        self._link_names_and_terms(names, terms)

    def _get_semantic_features(self, sentence):
        words = self.text_tools.get_words(sentence)
        text_blob = self.text_tools.text_blob(sentence)
        names = self.text_tools.get_all_entities(sentence)
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
        self._print_semantics(names, terms, sentiment, subjectivity)
        return names, terms, sentiment, subjectivity

    def _link_names_and_terms(self, names, terms):
        if len(names) > 0 and len(terms) > 0:
            for n in names:
                name = self.data_models.NounPhrase(n)
                for n2 in names:
                    name2 = self.data_models.NounPhrase(n2)
                    name.associate(name2)
                for t in terms:
                    term = self.data_models.UniqueTerm(t)
                    name.associate(term)
                    for t2 in terms:
                        term2 = self.data_models.UniqueTerm(t2)
                        term.associate(term2)

    def _get_semantic_stats(self, document):
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
            "neg_sentiments": len(neg_sentiment),
            "sentiment_mean":
                sum(self._all_sentiment)/len(self._all_sentiment),
            "subjectivity_mean":
                sum(self._all_subjectivity)/len(self._all_subjectivity)
        }
        document.set_node_properties(self._semantic_feats)
        self._print_out()
        self._set_counters()

    def _print_semantics(self, names, terms, sentiment, subjectivity):
        print "\n** named entities", names
        print "** unique terms", terms
        #print "** noun phrases", noun_phrases
        print "** sentiment", sentiment
        print "** subjectivity", subjectivity, '\n'

    def _print_out(self):
        print "\n---DOCUMENT SUMMARY---"
        for x in self._semantic_feats:
            print " %-30s%-25s%-20s" % (x, self._semantic_feats[x], "")
        print "---     SUMMARY   ---\n"

    def _set_counters(self):
        self._words_total = ""
        self._all_statements = []
        self._all_names = []
        self._all_terms = []
        self._all_nounphrases = []
        self._all_relations = []
        self._all_sentiment = []
        self._all_subjectivity = []