from utils import general_linguistic
from delve import document_parser
from data_models import models, cache
from interfaces import text_io
from interfaces import data_io
from interfaces import web
from interfaces import pinboard_api
from interfaces import hansard


class CacheInterface:
    def __init__(self):
        self.data_models = models
        self.cache_models = cache
        self.csv_handler = text_io.TextInput()
        self.web_handler = web
        self.pinboard_api = pinboard_api
        self.speech_tools = general_linguistic
        self.tfidf_model = general_linguistic.TfidfModel()
        self.hansard = hansard.TWFYHansard()
        self.tfidf_model.load()
        self.core_model = self.data_models.DataModel()
        self.g = self.core_model.g
        self.csv_to_df = data_io.read_csv
        self.parser = self._get_document_parser()

    def _get_document_parser(self):
        return document_parser.DocumentParser(
            self.g,
            self.data_models,
            self.speech_tools
        )
