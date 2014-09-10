import pinboard


class PinboardInterface:
    def __init__(self, username, pwd):
        self.all_tags = []
        self.pinboard_account = pinboard.open(username, pwd)
        self.get_all_tags()

    def get_links(self, idea, count=10):
        self.pinboard_links = self.pinboard_account.posts(tag=idea, count=count)
        print 'got links'
        #self.urls = [link['href'] for link in self.pinboard_links]
        return self.pinboard_links

    def get_all_tags(self):
        tags = self.pinboard_account.tags()
        self.all_tags = [tag['name'] for tag in tags]
        return self.all_tags

    def add(self, url, description, extended, tags):
        self.pinboard_account.add(url, description, extended, tags)