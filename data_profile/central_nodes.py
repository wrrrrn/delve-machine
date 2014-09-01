from data_profile import DataProfiler


class CentralNodes(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        self.node_types = [
            ("Document", "title"),
            ("Argument", "title"),
            ("Government Department", "noun_phrase"),
            ("Parliamentary Debate", "noun_phrase"),
            ("Act of Parliament", "title"),
            ("Policy Category", "title"),
            ("Policy Agenda", "title"),
            ("Unique Term", "term"),
            ("Member of Parliament", "noun_phrase"),
            ("Sentence", "sentence_id"),
            ("Political Party", "noun_phrase"),
            #("Statement", "statement"),
            ("Noun Phrase", "noun_phrase"),
            ("Named Entity", "noun_phrase")
            #("Relation", "relation")
        ]
        self.outgoing = ["outgoing", "-", "->"]
        self.incoming = ["incoming", "<-", "-"]
        print "[**] Highly Connected Nodes\n"

    def show_nodes(self):
        for node_type in self.node_types:
            print node_type[0]
            self._get_node_centrality(node_type, *self.outgoing)
            self._get_node_centrality(node_type, *self.incoming)
            print "\n"
        #for node_type in self.node_types:
        #    self._get_node_centrality(node_type, *self.incoming)

    def _get_node_centrality(self, node, direction, left, right):
        print " Top %s relationships" % direction
        search_string = """
            MATCH (n:`{0}`) {1}[rel]{2} ()
            RETURN n.{3}, type(rel) as rel_type, count(rel) as degree
            ORDER BY degree DESC
            LIMIT 5
            """.format(node[0], left, right, node[1])
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        for result in output:
            result_node, relationship, count = result[0], result[1], result[2]
            self._print_count(direction, relationship, count, result_node)

    def _print_count(self, direction, relationship, count, node):
        output = " %-10s%-20s%-10s" % (count, relationship, node)
        print output.encode('utf-8')
