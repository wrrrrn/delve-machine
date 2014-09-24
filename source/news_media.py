from source import CacheInterface
from time import sleep
import os


class CacheMedia(CacheInterface):
    OPML = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'input/feedly.opml'
    )

    def __init__(self):
        CacheInterface.__init__(self)
        self.text = self.speech_tools.TextHandler()
        self.html_handler = self.web_handler.HtmlInterface()
        self.opml = self.web_handler.OpmlInterface(CacheMedia.OPML)
        self.cache = self.cache_models.Media()
        self.cached_docs = [doc["link"] for doc in self.cache.collection.find()]

    def iterate_sources(self):
        for pub, entry, link, text, date in self.opml.iterate('Politics'):
            print '\n\n', entry, '\n', pub, '\n', link, '\n', date
            if not link in self.cached_docs:
                full_text = self._get_full_text(text, link)
                document = {
                    "publication": pub,
                    "title": entry,
                    "link": link,
                    "date": date,
                    "text": full_text
                }
                self.cache.write(document)
                sleep(0.5)
            else:
                print "Document cached"

    def _get_full_text(self, raw_content, link):
        raw_text = self.text.parse_raw_html(raw_content)
        if raw_text:
            words = self._get_words(raw_text)
            if len(words) < 75:
                print 'rss entry too short, checking the web'
                html = self.html_handler.get_url(link)
                if html:
                    online_text = self.text.parse_html(html)
                    if online_text:
                        raw_text = online_text
        return u'{0}'.format(raw_text)

    def _get_words(self, raw):
        words = self.text.get_words(
            raw,
            with_punctuation=False,
            remove_stopwords=True
        )
        return words

    def print_out(self, label, value):
        print " %-30s%-25s%-20s" % (label, value, "")
