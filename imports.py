from data_imports import ImportInterface
from data_imports import government_and_mps as government
from data_imports import members_of_parliament as mps
from data_imports import policy_agenda_codebook as codebook
from data_imports import news_current_events as current_events
from data_imports import acts_of_parliament as legislation
from data_imports import experimental_parser

import_machine = ImportInterface()
extended_models = ""


def import_government():
    new_government = government.ImportGovernment(
        import_machine.csv_handler,
        import_machine.g,
        extended_models,
        import_machine.speech_tools
    )
    new_government.import_all_departments()
    new_government.import_mp_details()


def import_codebook():
    new_codebook = codebook.ImportCodebook()
    new_codebook.import_codebook()


def import_mps():
    new_mps = mps.ImportMPs()
    #new_mps.import_mp_details()
    new_mps.import_mp_debates()


def import_current():
    new_current = current_events.ImportCurrent()
    new_current.iterate_opml()


def import_acts():
    new_acts = legislation.ImportActsOfParliament()
    new_acts.import_acts()


def test_new_import():
    sentence_level_analysis = True
    new_test = experimental_parser.ImportExperimentalParser(
        import_machine.web_handler,
        import_machine.g,
        extended_models,
        import_machine.speech_tools,
        import_machine.tfidf_model,
        sentence_level_analysis
    )
    new_test.parse_blog()

print "\n\nBegining document imports..."
#import_government()
#import_codebook()
#import_acts()
import_current()
import_mps()


# test_new_import()