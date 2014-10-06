from source import mps
from source import news_media
from source import parliament
from source import policy_agendas


print "\n\nBegining document imports..."


def codebook():
    research = policy_agendas.PolicyResearch()
    research.import_policies()


def members_of_parliament():
    members = mps.CacheMPs()
    members.import_mps()


def get_parliament():
    parl = parliament.ParliamentData()
    parl.import_acts()
    parl.import_votes()
    parl.import_debates()


def current_media():
    media = news_media.CacheMedia()
    media.iterate_sources()



codebook()
members_of_parliament()
get_parliament()
#current_media()

