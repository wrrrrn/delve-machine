from data_models import cache, core
from fuzzywuzzy import process
from data_models import models
from utils import general_linguistic
from web.controllers import documents
from utils.experimental_parser import ExperimentalParser

ALL_PARTIES_API = 'http://www.theguardian.com/politics/api/party/all/json'

model = core.DataModel()
debates = cache.Debates()
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
            words = text.get_words(d["text"])
            print d["title"], "\n", d["link"], "\n------------"
           # print "original:\n", d["text"], "\n------------"
           # print len(words), "summary:\n", ' '.join(summary[:3]), "\n------------"
           # print "custom:\n", ' '.join(custom[:3])
            print "\n\n\n"
        except ZeroDivisionError:
            pass


def test_parser():
    docs = cache.Media()
    parser = ExperimentalParser(general_linguistic)
    summerizer = general_linguistic.Summerizer()
    for d in docs.fetch_all(return_list=True):
        print "----\n", d["_id"], d["title"]
        #print d["text"]
        parser.parse_document(d["text"])


def test_doc():
    url = 'http://owni.eu/2012/08/27/where-are-the-post-wikileaks-digital-whistleblowers-assange/'
    entity = documents.DocumentController(url)
    if entity.exists:
        for m in entity.topic_mentions():
            print m


def test_increment():
    cache_list = [d["debate_id"] for d in debates.fetch_all(return_list=True)]
    print "\n---"
    print "cached:", len(cache_list)
    print cache_list[:10]
    print "\n---"
    imported = model.get_all_doc_ids("Parliamentary Debate")

    print "live:", len(imported)
    live = [record[0] for record in imported]
    print live[:10]
    cache_list.append(live[:10])
    print "\n---"
    to_import = [d for d in cache_list if d not in live]
    for d in live:
        if d in cache_list:
            print "found something imported"
    #print "to import:", len(to_import)


#test_parser()
#t# est_doc()
test_increment()









