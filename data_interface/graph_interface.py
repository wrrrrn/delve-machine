from py2neo import neo4j, rel, node
from py2neo.calendar import GregorianCalendar


class Graph_Database:
    def __init__(self):
        self.URI = 'http://localhost:7474/db/data/'
        self.neo4j = neo4j
        self.rel = rel
        self.graph = self.neo4j.GraphDatabaseService("http://localhost:7474/db/data/")
        self.node = node
        self.relationship = neo4j.Relationship
        #print '\nneo4j connection established\n', self.graph
        self.create_index()

    def create_index(self):
        self.time_index = self.graph.get_or_create_index(neo4j.Node, "TIME")
        self.calendar = GregorianCalendar(self.time_index)
        self.connections = self.graph.get_or_create_index(
            self.relationship, "connections"
        )
        # self.test = self.graph.get_or_create_index(self.node, "documents")
        indexes = [
            "CREATE INDEX ON :Document(link);",
            "CREATE INDEX ON :`Named Entity`(noun_phrase);",
            "CREATE INDEX ON :`Noun Phrase`(noun_phrase);",
            "CREATE INDEX ON :`Unique Term`(term);",
            "CREATE INDEX ON :Policy(link);",
            "CREATE INDEX ON :`Policy Category`(link);",
            "CREATE INDEX ON :Sentence(sentence_id);",
            "CREATE INDEX ON :`Parliamentary Debate`(link);",
            "CREATE INDEX ON :`Act of Parliament`(link);"
        ]
        for index in indexes:
            self.neo4j.CypherQuery(self.graph, index)



    # TODO: Convert this to a merge statement
    def create_relationship(self, start_node, relationship, end_node):
        return self.graph.create(rel(start_node, relationship, end_node))



