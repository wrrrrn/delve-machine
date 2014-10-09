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
            "Debate Argument",
            "Public Media",
            "Act of Parliament",
            "Policy Category",
            #"Statement",
            "Policy Agenda",
            "Sentence",
            "Unique Term",
            "Noun Phrase",
            "Named Entity",
            "Member of Parliament",
            "Term in Parliament",
            "Government Department",
            "Government Position",
            "Political Party",
            "Parliamentary Debate",
            "Parliamentary Vote",
            "Vote Category"
            #"Relation"
        ]