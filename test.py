from pyteaser import Summarize
from data_models import cache, core
from fuzzywuzzy import process
from data_models import models
from utils import general_linguistic
from web.controllers import documents
from web.controllers import named_entities
from web.controllers import unique_terms
from utils.experimental_parser import ExperimentalParser

ALL_PARTIES_API = 'http://www.theguardian.com/politics/api/party/all/json'

model = core.DataModel()
reps = cache.Politicians()
all_reps = [doc["full_name"] for doc in reps.collection.find() if "full_name" in doc]


def find_cached_mp(search):
    cand = process.extractOne(search, all_reps)
    result = reps.collection.find({"full_name": cand[0]}).limit(1)
    return result[0]


def find():
    news = cache.Media()
    text = general_linguistic.TextHandler()
    for d in news.fetch_all(return_list=True):
        try:
            summary = Summarize(d["title"], d["text"].encode('ascii', 'ignore'))
            custom = summerizer.summarize(d["title"], d["text"])
            words = text.get_words(d["text"])
            print d["title"], "\n", d["link"], "\n------------"
           # print "original:\n", d["text"], "\n------------"
            print len(words), "summary:\n", ' '.join(summary[:3]), "\n------------"
            print "custom:\n", ' '.join(custom[:3])
            print "\n\n\n"
        except ZeroDivisionError:
            pass


def test_parser():
    docs = cache.Media()
    parser = ExperimentalParser(general_linguistic)
    summerizer = general_linguistic.Summerizer()
    for d in docs.fetch_all(return_list=True):
        print "----\n", d["_id"], d["title"]
        print d["text"]
        parser.parse_document(d["text"])


def doc_test():
    url = 'http://chrishanretty.co.uk/blog/index.php/2014/09/13/what-can-deutsche-bank-possibly-mean/'
    doc = documents.DocumentController(url)
    properties = doc.get_properties()
    print properties


def name_test():
    exclude = ["Document"]
    names = ['Alex Cunningham', 'Alistair Brightman', 'Jim Dowd', 'David Cameron']
    for name in names:
        print "\n---"
        name = named_entities.NamedEntityController(name)
        if name.exists:
            print name.name, "\n-"
            name.show_properties()

        else:
            print "huh?"


def term_test():
    terms = ['tax']
    for term in terms:
        print "\n---"
        t = unique_terms.UniqueTermsController(term)
        if t.exists:
            print t.term, "\n-"
            t.show_properties()

#find()
#doc_test()
#name_test()
#term_test()
#find_id()
test_parser()









