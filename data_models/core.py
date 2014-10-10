from interfaces import graph
import calendar
import re


class DataModel:
    g = graph.GraphInterface()

    def __init__(self):
        self.g = DataModel.g
        self.vertex = None
        self.exists = False
        self.document_label = 'Document'
        self.named_label = "Named Entity"
        self.noun_label = "Noun Phrase"
        self.term_label = "Unique Term"
        self.policy_label = 'Policy Agenda'
        self.category_label = 'Policy Category'
        self.sentence_label = 'Sentence'
        self.statement_label = 'Statement'
        self.predicate_label = 'Relation'
        self.debate_label = 'Parliamentary Debate'
        self.vote_label = 'Parliamentary Vote'
        self.votecategory_label = 'Vote Category'
        self.act_label = 'Act of Parliament'
        self.argument_label = 'Debate Argument'

    def find_vertex(self, label, node_key, value):
        self.vertex = None
        search_query = u"""
                MATCH (v:`{0}` {{{1}:"{2}"}})
                RETURN v
            """.format(label, node_key, value)
        output = self.query(search_query)
        if output:
            return output[0][0]
        else:
            return None

    def create_vertex(self, label, node_key, value):
        self.vertex = None
        search_query = u"""
                MERGE (v:`{0}` {{{1}:"{2}"}})
                ON MATCH set v:`{0}`
                ON CREATE set v:`{0}`
                RETURN v
            """.format(label, node_key, value)
        output = self.query(search_query)
        self.vertex = output[0][0]
        self.vertex.add_labels(label)
        return self.vertex

    def set_node_properties(self, properties=None, labels=None):
        batch = self.g.neo4j.WriteBatch(self.g.graph)
        if properties:
            for prop in properties:
                batch.set_property(self.vertex, prop, properties[prop])
                #self.vertex.update_properties()
        if labels:
            if isinstance(labels, list):
                for label in labels:
                    self.vertex.add_labels(label)
            else:
                self.vertex.add_labels(labels)
        results = batch.submit()
        return results

    def create_relationship(self, vertex1, relationship, vertex2):
        #return self.g.create_relationship(vertex1, relationship, vertex2)
        rel_query = u"""
            START n=node({0}), m=node({1})
            MERGE (n)-[r:{2}]-(m)
            RETURN r
        """.format(vertex1._id, vertex2._id, relationship)
        return self.query(rel_query)

    def query(self, query_string):
        search = self.g.neo4j.CypherQuery(self.g.graph, query_string)
        return search.execute()

    def batch(self):
        batch = self.g.neo4j.WriteBatch(self.g)
        return batch

    def get_all_nodes(self, node_type):
        search_string = u"MATCH (n:`{0}`) RETURN n".format(node_type)
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def set_date(self, date, relationship):
        if '/' in date:
            d = date.split('/')
            month, day, year = int(d[0]), int(d[1]), int(d[2])
        elif '-' in date:
            d = date.split('-')
            year, month, day = int(d[0]), int(d[1]), int(d[2])
        self.create_relationship(
            self.vertex,
            relationship,
            self.g.calendar.day(year, month, day)
        )

    def convert_article_date(self, date):
        date = date.split(" ")
        if re.search('\d+', date[0]):
            day = date[0]
            month = date[1]
            year = date[2]
        else:
            day = date[1]
            month = date[2]
            year = date[3]
        #print day, month, year
        d = dict((v, k) for k, v in enumerate(calendar.month_abbr))
        return {"day": int(day), "month": d[month], "year": int(year)}

    def link_sentence(self, sentence_node):
        self.create_relationship(
            self.vertex,
            "CONTAINS",
            sentence_node
        )

    def link_names_to_sent(self, names, sentence_node):
        #batch testing
        batch = self.g.neo4j.WriteBatch(self.g.graph)
        noun_index = self.g.graph.get_or_create_index(self.g.neo4j.Node, "noun_phrases")
        for name in names:
            new_node = batch.get_or_create_in_index(
                self.g.neo4j.Node,
                noun_index,
                "noun_phrase",
                name,
                {"name": name, "noun_phrase": name}
            )
            batch.create(
                self.g.rel(sentence_node, "MENTIONS", new_node)
            )
            batch.add_labels(new_node, "Noun Phrase")
        batch.submit()

    def get_all_doc_ids(self, doc_type):
        doc_query = u"""
            MATCH (d:`{0}`)
            RETURN d.link
        """.format(doc_type)
        return self.query(doc_query)

class Document(DataModel):
    def __init__(self, link=False):
        DataModel.__init__(self)
        self.link = link
        self.label = self.document_label

    def fetch(self):
        if self.link:
            #self.content = self.vertex.content.replace('\n', '<br /><br />')
            self.vertex = self.find_vertex(
                self.label,
                'link',
                self.link
            )
            if self.vertex:
                self.exists = True

    def create(self):
        self.vertex = self.create_vertex(
            self.label,
            'link',
            self.link
        )

    def get_sentences(self):
        search_string = u"""
            MATCH (d:`Document`) WHERE d.link = "{0}" WITH d
            MATCH (d)-[:CONTAINS]->(s)
            return s
        """.format(self.vertex["link"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_doc_features(self, feature):
        search_string = u"""
            MATCH (d:`Document`) WHERE d.link = "{0}" WITH d
            MATCH (d)-[:CONTAINS]->(s) WITH s
            MATCH (s)-[:MENTIONS]->(feat:`{1}`) with feat
            RETURN feat, count(feat) as weight
            ORDER BY weight DESC
        """.format(self.vertex["link"], feature)
        output = self.query(search_string)
        for result in output:
            yield result[0], result[1]

    def update_content(self, content):
        self.vertex.content = self._format_content(content)

    def _format_content(self, string):
        old_content = string.split("\n\n")
        new_content = ""
        for para in old_content:
            new_content += u"<p>{0}</p>".format(para)
        return new_content

    def set_published_date(self, date):
        d = self.convert_article_date(date)
        self.create_relationship(
            self.vertex,
            "PUBLISHED",
            self.g.calendar.day(d['year'], d["month"], d["day"])
        )
