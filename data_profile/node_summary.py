from data_profile import DataProfiler


class NodeCount(DataProfiler):
    def __init__(self):
        DataProfiler.__init__(self)
        print "[**] Node Counts\n"

    def show_counts(self):
        self._get_total()
        self._get_relationships()
        print "-"
        for node_type in self.node_types:
            self._print_count(node_type, self._get_count(node_type))
        print "---"

    def _get_total(self):
        search_string = "MATCH (n) RETURN count(n) as count"
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        result = search_test.execute()
        self._print_count("TOTAL NODES", result[0][0])

    def _get_relationships(self):
        search_string = "MATCH ()-[n]-() RETURN count(n) as count"
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        result = search_test.execute()
        self._print_count("TOTAL RELATIONSHIPS", result[0][0])

    def _get_count(self, node_type):
        search_string = "MATCH (n:`%s`) RETURN count(n) as count" % node_type
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        result = search_test.execute()
        return result[0][0]

    def _print_count(self, label, count):
        print "%-25s%-5s" % (label, count)
