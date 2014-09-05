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

    # TODO: Convert this to a merge statement
    def create_relationship(self, start_node, relationship, end_node):
        return self.graph.create(rel(start_node, relationship, end_node))

    def create_relationship_index(self, start_node, relationship, end_node):
        """
        Not sure if I'm making, or even need to make, unique relationships.
        Leaving this here for later testing
        """
        return self.connections.get_or_create(
            "connection", relationship, (start_node, relationship, end_node)
        )

