
from xml.etree import ElementTree
import feedparser
import urllib2
import StringIO
import gzip
import calendar


class HtmlInterface:
    def __init__(self):
        self.excluded_urls = \
        ['http://www.philosophyofinformation.net/publications/pdf/htdpi.pdf']

    def get_url(self, content_url):
            if content_url not in self.excluded_urls:
                #print "getting url: %s" % content_url
                self.html = self.get_webpage(content_url)
                return self.html

    def get_webpage(self,  address):
        request = urllib2.Request(address)
        request.add_header('Accept-encoding', 'gzip')
        try:
            response = urllib2.urlopen(request)
            if response.info().get('Content-Encoding') == 'gzip':
                data = StringIO.StringIO(response.read())
                gzipper = gzip.GzipFile(fileobj=data)
                html = gzipper.read()
            else:
                html = response.read()
        except Exception, e:
            print e
            return False
        return html


class OpmlInterface:
    def __init__(self, opml):
        self.opml_file = opml
        self.site_feeds = []
        with open(self.opml_file, 'rt') as f:
            self.opml = ElementTree.parse(f)

    def get_section(self, section):
        self.site_feeds = []
        for node in self.opml.getiterator('outline'):
            for name, value in sorted(node.attrib.items()):
                if name == 'text' and value == section:
                    for specific_node in node.getiterator():
                        title = specific_node.attrib.get('text')
                        url = specific_node.attrib.get('xmlUrl')
                        if name and url:
                            self.site_feeds.append((title, url))
        return self.site_feeds

    def iterate(self, section):
        for title, url in self.get_section(section):
            rss = RssInterface(url)
            blog = rss.parse_rss()
            for entry in blog.entries:
                if hasattr(entry, 'description'):
                    if hasattr(entry, 'published'):
                        date = self.cleanup_date(entry.published)
                    else:
                        date = "01 Jan 0001"
                    yield blog.feed.title,\
                        entry.title,\
                        entry.link,\
                        entry.description,\
                        date

    def cleanup_date(self, date):
        if " " in date:
            new_date = date.split(" ")
            return " ".join(new_date[1:4])
        elif "T" in date:
            temp = date.split("T")
            new = temp[0].split("-")
            temp = new[2], calendar.month_name[int(new[1])][:3], new[0]
            return " ".join(temp)


class RssInterface:
    def __init__(self, rss_input):
        self.rss_input = rss_input

    def parse_rss(self):
        return feedparser.parse(self.rss_input)
