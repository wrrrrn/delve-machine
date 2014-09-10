
import readability


class ReadabilityInterface:
    def __init__(self, key, secret, username, pwd):
        self.token = readability.xauth(key, secret, username,pwd)
        self.rdd = readability.oauth(key, secret, token=self.token)

    def get_bookmarks_detail(self):
        return [
            (b.article.url, b.article.title, b.article.excerpt)
            for b
            in self.rdd.get_bookmarks()
        ]
        #return self.rdd.get_bookmarks()