from delve import ImportInterface


class ImportMedia(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Media()
        self.text = self.speech_tools.TextHandler()

    def delve(self):
        for doc in self.cache.collection.find():
            self._import(doc)

    def _import(self, node):
        publication = node["publication"]
        title = node["title"]
        link = node["link"]
        date = node["date"]
        publication = node["publication"]
        text = node["text"]
        print '\n\n', publication, '\n', title, '\n', link, '\n', date
        cleaned_text = self._get_text(text)
        article = self._create_article_node(
            publication,
            title,
            link,
            cleaned_text,
            date
        )
        self.parser.parse_document(article, cleaned_text, map_statements=False)

    def _create_article_node(self, publication, title, link, content, date):
        new_document = self.data_models.Document(link)
        if not new_document.exists:
            new_document.create()
            labels = "Public Media"
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

    def _get_text(self, raw_content):
        scrubbed_text = self.text.parse_raw_html(raw_content)
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