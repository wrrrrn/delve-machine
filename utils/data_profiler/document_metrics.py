from __future__ import division


class PopulationStatistics:
    def __init__(self, models, text_io, sem):
        self.data_models = models
        self.csv_out = text_io.MetricsOutput()
        self.semantic_tools = sem

    def get_documents(self):
        document_model = self.data_models.Document()
        all_documents = document_model.get_all_documents()
        for result in all_documents:
            document = result
            #print document["title"]
            self.csv_out.document_data["title"] = document["title"]
            self.csv_out.document_data["sentence_total"] = document["sentence_total"]
            self.csv_out.document_data["words_total"] = document["words_total"]
            self.csv_out.document_data["words_unique"] = document["words_unique"]
            self.csv_out.document_data["words_diversity"] = document["words_diversity"]
            self.csv_out.document_data["sentiment_total"] = document["sentiment_total"]
            self.csv_out.document_data["sentiment_mean"] = document["sentiment_mean"]
            self.csv_out.document_data["pos_sentiments"] = document["pos_sentiments"]
            self.csv_out.document_data["neg_sentiments"] = document["neg_sentiments"]
            self.csv_out.document_data["neu_sentiments"] = document["neu_sentiments"]
            self.csv_out.document_data["subjectivity_total"] = document["subjectivity_total"]
            self.csv_out.document_data["subjectivity_mean"] = document["subjectivity_mean"]
            self.csv_out.document_data["named_entity_count"] = document["named_entity_count"]
            self.csv_out.document_data["named_entity_unique"] = document["named_entity_unique"]
            self.csv_out.document_data["statement_count"] = document["statement_count"]
            self.csv_out.document_data["relations_unique"] = document["relations_unique"]
            self.csv_out.document_data["noun_phrase_count"] = document["noun_phrase_count"]
            self.csv_out.document_data["noun_phrase_unique"] = document["noun_phrase_unique"]
            self.csv_out.document_data["nounphrase_common"] = document["nounphrase_common"]
            self.csv_out.document_data["link"] = document["link"]
            try:
                self.csv_out.document_data["word_per_sent"] = \
                    self.csv_out.document_data["words_total"]/self.csv_out.document_data["sentence_total"]
            except TypeError:
                self.csv_out.document_data["word_per_sent"] = 0
            self.csv_out.write_to_csv()

    def print_out(self, label, value):
        print " %-15s%-5s%-15s" % (label, value, "")
