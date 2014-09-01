from data_profile import DataProfiler


class SentenceNodes(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        print "Sentence Sentiment & Objectivity Scores"

    def show_counts(self):
        print "Sentiment"
        positive = self._get_sentence_overview("sentiment", ">", "0")
        self._print_count("Positive", positive)
        negative = self._get_sentence_overview("sentiment", "<", "0")
        self._print_count("Negative", negative)
        neutral = self._get_sentence_overview("sentiment", "=", "0")
        self._print_count("Neutral", neutral)
        print "Subjectivity"
        positive = self._get_sentence_overview("subjectivity", ">", "0.5")
        self._print_count("Subjective", positive)
        negative = self._get_sentence_overview("subjectivity", "<", "0.5")
        self._print_count("Objective", negative)
        print "---"

    def _get_sentence_overview(self, type, polarity, median):
        search_string = """
            MATCH (n:`Sentence`)
            WHERE n.{0} {1} {2}
            RETURN count(n)
            """.format(type, polarity, median)
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        result = search_test.execute()
        return result[0][0]

    def _print_count(self, type, count):
        output = " %-15s%-20s%-10s" % (type, count, "")
        print output.encode('utf-8')
