from source import mps
from source import policy_agenda_codebook
from source import news_current_events
from source import acts_of_parliament
from source import parliament_debates
from source import parliament


print "\n\nBegining document imports..."


def codebook():
    new_codebook = policy_agenda_codebook.ImportCodebook()
    new_codebook.import_codebook()


def members_of_parliament():
    members = mps.GetMPs()
    members.import_mps()


def get_parliament():
    #stuff = parliament_debates.Parliament()
    #stuff.import_debates()
    parl = parliament.ParliamentData()
    #parl.import_acts()
    #parl.import_votes()
    parl.import_debates()


def current_media():
    new_current = news_current_events.ImportCurrent()
    new_current.iterate_opml()


def acts():
    new_acts = acts_of_parliament.ImportActsOfParliament()
    new_acts.import_acts()


#codebook()
#acts()
#members_of_parliament()
#current_media()
get_parliament()
