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
        fresh = [doc["full_name"] for doc in self.cache.collection.find()]
        publication = node["publication"]
        title = node["title"]
        link = node["link"]
        date = node["date"]
        text = node["publication"]
        print '\n\n', publication, '\n', title, '\n', link, '\n', date
        cleaned_text = self._get_text(text, link)
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
