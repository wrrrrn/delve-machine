from fuzzywuzzy import process

from data_models import core, models, cache
from utils import general_linguistic
from web.controllers import documents
from web.controllers import mps
from web.api import mps_api
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
    url = '54234698e226df11893507ec'
    entity = documents.DocumentController(url)
    if entity.exists:
        print "yes"
        print entity.show_properties()
        for n in entity.associated_names():
            print n
        for t in entity.associated_topics():
            print t
    else:
        print "huh?"


def test_mp_aggr():
    mp_aggregator = mps_api.MpAggregateController()
    for p in mp_aggregator.government():
        print p


def test_mp():
    name = "Mark Durkan"
    mp = models.MemberOfParliament(name)
    print mp.positions
    print mp.departments


def test_mps():
    mps = mps_api.MpsApi()
    print mps.get_all()

#test_parser()
#test_doc()
#test_mp_aggr()
test_mps()











