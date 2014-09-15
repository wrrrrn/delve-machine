from data_models import models
from interfaces import text_io


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
            "Unique Term",
            "Noun Phrase",
            "Named Entity",
            "Act of Parliament",
            "Member of Parliament",
            "Term in Parliament",
            "Government Department",
            "Government Position",
            "Political Party",
            "Parliamentary Debate"
            #"Relation"
        ]