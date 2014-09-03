from data_models import models
from data_interface import text_io


class DataProfiler:
    def __init__(self):
        self.data_models = models
        self.core_model = self.data_models.DataModel()
        self.g = self.core_model.g
        self.csv_handler = text_io.TextInput()
        self.node_types = [
            "Document",
            "Argument",
            "Policy Category",
            "Sentence",
            #"Statement",
            "Policy Agenda",
            "Parliamentary Debate",
            "Noun Phrase",
            "Unique Term",
            "Named Entity",
            "Political Party",
            "Government Department",
            "Government Position",
            "Member of Parliament",
            "Political Party"
            #"Relation"
        ]