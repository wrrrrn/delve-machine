from data_imports import mps
from data_imports import policy_agenda_codebook
from data_imports import news_current_events
from data_imports import acts_of_parliament
from data_imports import parliament_debates


print "\n\nBegining document imports..."


def codebook():
    new_codebook = policy_agenda_codebook.ImportCodebook()
    new_codebook.import_codebook()


def members_of_parliament():
    new_mps = mps.ImportMPs()
    new_mps.import_mp_details()


def get_parliament():
    stuff = parliament_debates.Parliament()
    stuff.import_debates()


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
