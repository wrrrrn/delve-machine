from goose import Goose
from textblob import TextBlob
from analytical_tools import relations


class ImportExperimentalParser:
    def __init__(self, web_handler, database, models,
                    speech_tools, tfidf, atomic):
        self.relation_extractor = relations.Relations()
        self.goose = Goose()
        self.analyse_to_sentence = atomic
        self.web_handler = web_handler
        self.g = database
        self.core_model = models.DataModel(self.g)
        self.extended_models = models
        self.speech_tools = speech_tools
        self.text = speech_tools.TextHandler()
        self.tfidf = tfidf
        self.text_blob = TextBlob
        self.connect_to_web_services()

    def connect_to_web_services(self):
        self.html_handler = self.web_handler.HtmlHandler()
        self.opml_file = 'data_imports/input/google-reader-subscriptions.xml'
        self.opml = self.web_handler.Opml(self.opml_file)

    def parse_blog(self):
        politics_blogs = self.opml.get_section('Politics')
        blog_name = 'pinboard.in/u:wrrn'
        date = "01 Jan 0001"
        rss = self.web_handler.Rss(politics_blogs[28][1])
        blog = rss.parse_rss()
        for entry in blog.entries:
            print "\n\n---\nTitle: %s\nLink: %s" % (entry['title'], entry['link'])
            try:
                raw_html = entry['content'][0]['value']
            except KeyError:
                raw_html = entry['summary_detail']['value']
            cleaned_text = self.get_text(raw_html, entry['link'])
            article = self.create_article_node(
                blog_name,
                entry['title'],
                entry['link'],
                cleaned_text,
                date)
            # print cleaned_text
            # self.display_graph_objects(cleaned_text)
            self.parse_document(article, cleaned_text)

    def display_graph_objects(self, text):
        if self.analyse_to_sentence:
            print '--\n\n [x] mapping objects at sentence level...'
            content = self.text_blob(text)
            # sentences = self.text.get_sentences(text)
            for s in content.sentences:
                print s
                self.map_relations(s)

    def create_article_node(self, publication, title, link, content, date):
        new_article = self.extended_models.Article(link, db=self.g)
        if not new_article.exists:
            new_article.get_or_create_node()
            new_article.vertex["publication"] = publication
            new_article.vertex["title"] = title
            new_article.vertex["content"] = content
            new_article.vertex.add_labels("Article")
            print '  [x] Article created...'
        new_article.set_published_date(date)
        return new_article

    def parse_document(self, article, document):
        # content = self.text_blob(document)
        sentences = self.text.get_sentences(document)
        for sentence_number, s in enumerate(sentences):
            print s
            sentence_id = "%s::%s" % (article.vertex["link"], sentence_number)
            sentence = self.create_sentence_node(sentence_id)
            if not sentence.exists:
                sentence.get_or_create_node()
                sentence.vertex["sentence"] = s
            self.core_model.create_relationship(
                article.vertex,
                "CONTAINS",
                sentence.vertex
            )
            if sentence_number > 0:
                prev_sentence_id = "%s::%s" % (
                    article.vertex["link"], sentence_number-1
                )
                prev_sentence = self.create_sentence_node(prev_sentence_id)
                if prev_sentence.exists:
                    self.core_model.create_relationship(
                        prev_sentence.vertex,
                        "NEXT",
                        sentence.vertex
                    )
                else:
                    print '  [O] Could not find the previous sentence', prev_sentence_id
            self.map_relations(sentence.vertex, s)

    def create_sentence_node(self, id):
        return self.extended_models.Sentence(id, db=self.g)

    def parse_semantics(self, text):
        words = self.get_words(text)
        tfidf_results = self.tfidf.classify(words, score=False)
        unique_terms = self.speech_tools.unique_list(tfidf_results)
        name_entities = self.text.get_all_entities(text)
        unique_names = self.speech_tools.unique_list(name_entities)
        results = {
            'text': text,
            'names': unique_names,
            'terms': unique_terms
        }
        #  print "---\n* text:", text
        print "* names:", unique_names
        print "* terms:", unique_terms
        return results

    def map_relations(self, sentence_node, text):
        text_blob = self.text_blob(text)
        verbs = [x for x in text_blob.pos_tags if 'VB'in x[1]]
        names = self.text.get_all_entities(text)
        print "** named entities", names
        print "** noun phrases", text_blob.noun_phrases
        print "** verbs", verbs
        # print "** pos", text.pos_tags, '\n'
        print "** sentiment", text_blob.sentiment.polarity
        print "** subjectivity", text_blob.sentiment.subjectivity, '\n'
        sentence_node["sentiment"] = text_blob.sentiment.polarity
        sentence_node["subjectivity"] = text_blob.sentiment.subjectivity
        for name in names:
            new_name = self.extended_models.NounPhrase(name, db=self.g)
            if not new_name.exists:
                new_name.get_or_create_node()
            new_name.vertex.add_labels(new_name.named_label)
            self.core_model.create_relationship(
                sentence_node,
                "MENTIONS",
                new_name.vertex
            )
        relations = self.relation_extractor.extract_triples(
            text, lex_syn_constraints=True
        )
        self.map_statement(sentence_node, relations)

    def map_statement(self, sentence, relations):
        for i, relation in enumerate(relations):
            sub, rel, obj = relation
            print "** relations:", sub, '->', rel, '->', obj
            statement = "%s %s %s" % (sub, rel, obj)
            statement_id = "%s::%s" % (
                sentence["sentence_id"], i
            )
            statement_node = self.extended_models.Statement(statement_id, db=self.g)
            if not statement_node.exists:
                statement_node.get_or_create_node()
                statement_node.vertex["statement"] = statement
            self.core_model.create_relationship(
                sentence,
                "CONTAINS",
                statement_node.vertex
            )
            new_subject = self.extended_models.NounPhrase(sub, db=self.g)
            if not new_subject.exists:
                new_subject.get_or_create_node()
            new_subject.vertex.add_labels("Subject")
            self.core_model.create_relationship(
                statement_node.vertex,
                "IS_COMPOSED_OF",
                new_subject.vertex
            )
            new_object = self.extended_models.NounPhrase(obj, db=self.g)
            if not new_object.exists:
                new_object.get_or_create_node()
            new_object.vertex.add_labels("Object")
            self.core_model.create_relationship(
                statement_node.vertex,
                "IS_COMPOSED_OF",
                new_object.vertex
            )
            new_predicate = self.extended_models.Predicate(rel, db=self.g)
            if not new_predicate.exists:
                new_predicate.get_or_create_node()
            self.core_model.create_relationship(
                statement_node.vertex,
                "IS_COMPOSED_OF",
                new_predicate.vertex
            )
            self.core_model.create_relationship(
                new_subject.vertex,
                "ASSERTS",
                new_predicate.vertex
            )
            self.core_model.create_relationship(
                new_predicate.vertex,
                "RELATED_TO",
                new_object.vertex
            )
        print '\n'

    def get_text(self, raw_content, link):
        scrubbed_text = self.text.parse_raw_html(raw_content)
        if scrubbed_text:
            words = self.get_words(scrubbed_text)
            if len(words) < 75:
                print 'rss entry too short, checking the web'
                html = self.html_handler.get_url(link)
                if html:
                    online_text = self.text.parse_html(html)
                    if online_text:
                        scrubbed_text = online_text
        return scrubbed_text

    def get_words(self, raw):
        words = self.text.get_words(
            raw,
            with_punctuation=False,
            remove_stopwords=True
        )
        return words