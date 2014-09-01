from analytical_tools import relations


class DocumentParser:
    def __init__(self, database, models, speech_tools):
        self.g = database
        self.relation_extractor = relations.Relations()
        self.core_model = models.DataModel()
        self.data_models = models
        self.speech_tools = speech_tools
        self.text_tools = self.speech_tools.TextHandler()
        self.tfidf_model = self.speech_tools.TfidfModel()
        self.tfidf_model.load()
        self._set_counters()
        self._semantic_feats = []

    def parse_document(self, document, content, map_statements=True):
        # content = self.text_blob(document)
        # text = content.
        self.map_statements = map_statements
        bag_of_words = self.text_tools.get_words(
            content,
            with_punctuation=False,
            remove_stopwords=True
        )
        self._words_total = len(bag_of_words)
        sentences = self.text_tools.get_sentences(content)
        for sentence_number, s in enumerate(sentences):
            print s
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
            self._map_semantics(sentence, s)
            if self.map_statements:
                self._map_statement(sentence, s)
        self._get_semantic_stats(document)

    def _create_sentence_node(self, sentence_id, sentence):
        sentence_node = self.data_models.Sentence(sentence_id)
        if not sentence_node.exists:
            sentence_node.create()
            sentence_node.vertex["sentence"] = sentence
        return sentence_node

    def _map_semantics(self, sentence, text):
        names, terms, sentiment, subjectivity = self._get_semantics(text)
        sentence.vertex["sentiment"] = sentiment
        sentence.vertex["subjectivity"] = subjectivity
        # batch_names = self.data_models.NounPhrase(None)
        # roll this back to pre-batch
        # batch_names.link_names_to_sent(names, sentence_node)
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

    def _link_names_and_terms(self, names, terms):
        if len(names) > 0 and len(terms) > 0:
            for n in names:
                name = self.data_models.NounPhrase(n)
                for t in terms:
                    term = self.data_models.UniqueTerm(t)
                    name.link_term(term)

    def _get_semantics(self, sentence):
        words = self.text_tools.get_words(sentence)
        text_blob = self.text_tools.text_blob(sentence)
        names = self.text_tools.get_all_entities(sentence)
        # noun_phrases = text_blob.noun_phrases
        sentiment = text_blob.sentiment.polarity
        subjectivity = text_blob.sentiment.subjectivity
        tfidf_results = self.tfidf_model.classify(words, score=False)
        terms = self.speech_tools.unique_list(tfidf_results)
        if len(names) > 0:
            self._all_names.extend(names)
        if len(terms) > 0:
            self._all_terms.extend(terms)
        self._all_sentiment.extend([sentiment])
        self._all_subjectivity.extend([subjectivity])
        print "\n** named entities", names
        print "** unique terms", terms
        #print "** noun phrases", noun_phrases
        print "** sentiment", sentiment
        print "** subjectivity", subjectivity, '\n'
        return names, terms, sentiment, subjectivity

    def _map_statement(self, sentence, text):
        new_relations = self._get_statement(text)
        for i, relation in enumerate(new_relations):
            sub, rel, obj = relation
            self._all_nounphrases.extend([sub, obj])
            self._all_relations.extend([rel])
            print "** relations:", sub, '->', rel, '->', obj
            extracted_statement = "%s %s %s" % (sub, rel, obj)
            statement_id = "%s::%s" % (
                sentence.vertex["sentence_id"], i
            )
            self._all_statements.extend([extracted_statement])
            statement = self.data_models.Statement(statement_id)
            if not statement.exists:
                statement.create()
                statement.vertex["statement"] = extracted_statement
            sentence.link_statement(statement)
            statement.link_elements(sub, rel, obj)
        print '\n'

    def _get_statement(self, text):
        new_relations = self.relation_extractor.extract_triples(
            text, lex_syn_constraints=True
        )
        return new_relations

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
        if self.map_statements:
            noun_phrase_unique = len(
                self.text_tools.unique_lemmas(self._all_nounphrases)
            )
            self._semantic_feats["noun_phrase_count"] = noun_phrase_unique
            self._semantic_feats["relations_unique"] = len(self._all_relations)
            self._semantic_feats["statement_count"] = len(self._all_statements)
        document.set_node_properties(self._semantic_feats)
        self._print_out()
        self._set_counters()

    def _print_out(self):
        print "---DOCUMENT SUMMARY---"
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