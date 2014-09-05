from data_imports import members_of_parliament
from data_imports import policy_agenda_codebook
from data_imports import news_current_events
from data_imports import acts_of_parliament


print "\n\nBegining document imports..."


def codebook():
    new_codebook = policy_agenda_codebook.ImportCodebook()
    new_codebook.import_codebook()


def mps():
    new_mps = members_of_parliament.ImportMPs()
    new_mps.import_mp_details()
    #new_mps.import_mp_debates()


def current_media():
    new_current = news_current_events.ImportCurrent()
    new_current.iterate_opml()


def acts():
    new_acts = acts_of_parliament.ImportActsOfParliament()
    new_acts.import_acts()


codebook()
acts()
mps()
current_media()
