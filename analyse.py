from delve import mps
from delve import news_media
from delve import policy_agendas
from delve import legislation
from delve import debates
from delve import votes


def codebook():
    p = policy_agendas.ImportPolicies()
    p.delve()


def members_of_parliament():
    m = mps.ImportMPs()
    m.delve()


def get_votes():
    v = votes.ImportVotes()
    v.delve()


def get_debates():
    d = debates.ImportDebates()
    d.delve()


def get_acts():
    acts = legislation.ImportActs()
    acts.delve()


def current_media():
    media = news_media.ImportMedia()
    media.delve()

print "Delve. Politic"

codebook()
members_of_parliament()
get_acts()
get_votes()
current_media()
get_debates()



