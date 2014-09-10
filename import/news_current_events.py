from data_imports import document_parser, ImportInterface


class ImportCurrent(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.text = self.speech_tools.TextHandler()
        self._connect_to_web_services()

    def _connect_to_web_services(self):
        #opml_file = 'import/input/google-reader-subscriptions.xml'
        opml_file = 'import/input/feedly.xml'
        self.html_handler = self.web_handler.HtmlInterface()
        self.opml = self.web_handler.OpmlInterface(opml_file)

    def iterate_opml(self):
        for blog, entry, link, text, date in self.opml.iterate('Politics'):
            print '\n\n', blog, '\n', entry, '\n', link, '\n', date
            cleaned_text = self._get_text(text, link)
            article = self._create_article_node(blog, entry, link, cleaned_text, date)
            parser = self._get_document_parser()
            parser.parse_document(article, cleaned_text, map_statements=False)

    def _get_document_parser(self):
        return document_parser.DocumentParser(
            self.g,
            self.data_models,
            self.speech_tools,
        )

    def _create_article_node(self, publication, title, link, content, date):
        new_document = self.data_models.Document(link)
        if not new_document.exists:
            new_document.create()
            labels = "Media"
            properties = {
                "publication": publication,
                "title": title,
                "content": content
            }
            new_document.set_node_properties(
                properties,
                labels
            )
            print '#', title, 'created...'
        new_document.set_published_date(date)
        return new_document

    def _get_text(self, raw_content, link):
        scrubbed_text = self.text.parse_raw_html(raw_content)
        if scrubbed_text:
            words = self._get_words(scrubbed_text)
            if len(words) < 75:
                print 'rss entry too short, checking the web'
                html = self.html_handler.get_url(link)
                if html:
                    online_text = self.text.parse_html(html)
                    if online_text:
                        scrubbed_text = online_text
        # convert input to ascii
        return scrubbed_text.encode('ascii', 'ignore')

    def _get_words(self, raw):
        words = self.text.get_words(
            raw,
            with_punctuation=False,
            remove_stopwords=True
        )
        return words

    def print_out(self, label, value):
        print " %-30s%-25s%-20s" % (label, value, "")
