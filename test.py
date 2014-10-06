from data_models import cache, core
from fuzzywuzzy import process
from data_models import models
from utils import general_linguistic
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



#find()
#doc_test()
#name_test()
#term_test()
#find_id()
test_parser()









