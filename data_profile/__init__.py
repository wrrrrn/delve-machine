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
            "Sentence",
            "Policy Category",
            #"Statement",
            "Policy Agenda",
            "Noun Phrase",
            "Named Entity",
            "Unique Term",
            "Act of Parliament",
            "Member of Parliament",
            "Political Party",
            "Parliamentary Debate",
            "Government Department",
            "Government Position"
            #"Relation"
        ]