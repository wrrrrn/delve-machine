import document_parser
from utils import general_linguistic
from interfaces import web
from data_models import models
from data_models import cache


class ImportInterface:
    def __init__(self):
        self.data_models = models
        self.cache_models = cache
        self.core_model = self.data_models.DataModel()
        self.g = self.core_model.g
        self.speech_tools = general_linguistic
        self.html_handler = web.HtmlInterface()
        self.parser = self._get_document_parser()

    def _get_document_parser(self):
        return document_parser.DocumentParser(
            self.g,
            self.data_models,
            self.speech_tools
        )