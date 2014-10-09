from data_models import cache
from data_models import core

graph_model = core.DataModel()
politicians = cache.Politicians()
votes = cache.Votes()
legislation = cache.Legislation()
debates = cache.Debates()
agendas = cache.PolicyAgenda()


def delete_all_cached():
    politicians.delete_data()
    votes.delete_data()
    legislation.delete_data()
    debates.delete_data()
    agendas.delete_data()


def delete_terms():
    list = [
        "get", "-", "d", "j", "233", "hon", "8212", "would", "163", "also", "1", "could", "might",
        "put", "8217", "said", "8221", "8220", "got", "says"
    ]
    for t in list:
        string = u"""
            MATCH (t:`Unique Term` {{term:"{0}"}})-[r]-(x)
            DELETE t,r
        """.format(t)
        output = graph_model.query(string)
        print output


def delete_names():
    list = [
        "Friend", "Gentlemen", "Lady", "8221", "8220", "got"
    ]
    for t in list:
        string = u"""
            MATCH (t:`Noun Phrase` {{noun_phrase:"{0}"}})-[r]-(x)
            DELETE t,r
        """.format(t)
        output = graph_model.query(string)
        print output



#delete_all_cached()

delete_terms()
#delete_names()
