import document_parser
from utils import general_linguistic
from interfaces import web
from data_models import core, cache
from data_models import models


class ImportInterface:
    def __init__(self):
        self.core_model = core
        self.data_models = models
        self.cache_models = cache
        self.core_model = self.data_models.DataModel()
        self.g = self.core_model.g
        self.speech_tools = general_linguistic
        self.html_handler = web.HtmlInterface()
        self.parser = self._get_document_parser()
        self.summerizer = general_linguistic.Summerizer()

    def _get_document_parser(self):
        return document_parser.DocumentParser(
            self.g,
            self.data_models,
            self.speech_tools
        )

    def _initialise(self, doc_type, cache_documents):
        cache_list = []
        live_docs = self.core_model.get_all_doc_ids(doc_type)
        live_list = [record[0] for record in live_docs]
        if doc_type == "Parliamentary Debate":
            cache_list = [d["debate_id"] for d in cache_documents]
        elif doc_type == "Public Media":
            cache_list = [d["link"] for d in cache_documents]
        to_import = [d for d in cache_list if d not in live_list]
        print "\nImporting", doc_type, "\n---"
        self._print_out("Cached Documents", len(cache_list))
        self._print_out("Live Documents", len(live_list))
        self._print_out("To Import", len(to_import))
        print "---\n"
        print cache_list[:3]
        print live_list[:3]
        return to_import

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)