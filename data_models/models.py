from core import DataModel
from core import Document


class Sentence(DataModel):
    def __init__(self, sentence_id):
        DataModel.__init__(self)
        self.sentence_id = sentence_id
        self.fetch()

    def fetch(self):
        self.exists = self.find_vertex(
            self.sentence_label,
            'sentence_id',
            self.sentence_id
        )
        if self.exists:
            self.vertex = self.exists
            self.exists = True

    def create(self):
        self.vertex = self.create_vertex(
            self.sentence_label,
            'sentence_id',
            self.sentence_id
        )
        self.exists = True

    def link_previous(self, sentence):
        self.create_relationship(
            sentence.vertex,
            "NEXT",
            self.vertex
        )

    def link_statement(self, statement):
        self.create_relationship(
            self.vertex,
            "CONTAINS",
            statement.vertex
        )

    def get_statements(self):
        search_string = \
            'MATCH (n:`Sentence` {sentence_id:"%s"})-[]->(x:`Statement`) ' \
            "return x" % self.sentence_id
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        for result in output:
            yield result[0]

    def get_statement_parts(self, part_type):
        search_string = \
            'MATCH (n:`Sentence` {sentence_id:"%s"})-[]->(x:`Statement`)-[]->(y:`%s`) ' \
            "return  y " % (self.sentence_id, part_type)
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        for result in output:
            yield result[0]


class NounPhrase(DataModel):
    def __init__(self, noun_phrase=False):
        DataModel.__init__(self)
        self.noun_phrase = noun_phrase
        self.label = self.noun_label
        self.fetch()

    def fetch(self):
        if self.noun_phrase:
            self.vertex = self.find_vertex(
                self.label,
                'noun_phrase',
                self.noun_phrase
            )
            if self.vertex:
                self.exists = True

    def create(self):
        self.vertex = self.create_vertex(
            self.label,
            'noun_phrase',
            self.noun_phrase
        )
        self.exists = True

    def link_sentence(self, sentence):
        self.create_relationship(sentence.vertex, "MENTIONS", self.vertex)

    def link_term(self, term):
        self.create_relationship(self.vertex, "IS_ASSOCIATED_WITH", term.vertex)

    def get_relationships(self, relationship):
        search_string = """
            MATCH (n:`Noun Phrase` {noun_phrase:"%s"})-[rel:`%s`]->()
            RETURN rel
        """ % (self.vertex["noun_phrase"], relationship)
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_documents(self):
        search_string = """
            MATCH (np:`Noun Phrase` {noun_phrase:"%s"})<-[:MENTIONS]-(s)
            WITH s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """ % (self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_associated_documents(self):
        search_string = """
            MATCH (np:`Noun Phrase` {noun_phrase:"%s"} )-[:IS_ASSOCIATED_WITH]-(t)
            WITH t
            MATCH (t)<-[:MENTIONS]-(s) with s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """ % (self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_sentences(self):
        search_string = """
            MATCH (np:`Noun Phrase` {noun_phrase:"%s"})<-[:MENTIONS]-(s)
            RETURN DISTINCT s
        """ % (self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_stats(self):
        search_string = """
            MATCH (t:`Noun Phrase` {noun_phrase:"%s"})<-[:MENTIONS]-(s)
            WITH s, count(s) as cs
            MATCH (s)-[:CONTAINS]-(d)
            WITH cs, count(d) as cd
            RETURN sum(cs), sum(cd)
        """ % (self.vertex["noun_phrase"])
        output = self.query(search_string)
        sent_count, doc_count = output[0][0], output[0][1]
        rel_count = len(
            [x for x in self.get_relationships("IS_ASSOCIATED_WITH")]
        )
        return sent_count, doc_count, rel_count


class MemberOfParliament(NounPhrase):
    def __init__(self, name):
        NounPhrase.__init__(self)
        self.noun_phrase = name
        self.label = self.noun_label
        self.fetch()

    def update_mp_details(self, properties=None):
        labels = ["Named Entity", "Member of Parliament"]
        self.set_node_properties(
            properties,
            labels
        )

    def link_position(self, position):
        self.create_relationship(self.vertex, "IN_POSITION", position.vertex)

    def link_department(self, department):
        self.create_relationship(self.vertex, "MEMBER_OF", department.vertex)

    def link_party(self, party):
        party = NounPhrase(party)
        labels = ["Named Entity", "Political Party"]
        if not party.exists:
            party.create()
        party.set_node_properties(labels=labels)
        self.create_relationship(self.vertex, "MEMBER_OF", party.vertex)


class GovernmentDepartment(NounPhrase):
    def __init__(self, name):
        NounPhrase.__init__(self)
        self.noun_phrase = name
        self.label = self.noun_label
        self.fetch()

    def update_details(self, details=None):
        labels = ["Named Entity", "Government Department"]
        properties = details
        self.set_node_properties(
            properties,
            labels
        )


class GovernmentPosition(NounPhrase):
    def __init__(self, name):
        NounPhrase.__init__(self)
        self.noun_phrase = name
        self.label = self.noun_label
        self.fetch()

    def update_details(self, details=None):
        labels = ["Named Entity", "Government Position"]
        properties = details
        self.set_node_properties(
            properties,
            labels
        )


class UniqueTerm(DataModel):
    def __init__(self, term):
        DataModel.__init__(self)
        self.term = term
        self.fetch()

    def fetch(self):
        self.exists = self.find_vertex(
            self.term_label,
            'term',
            self.term
        )
        if self.exists:
            self.vertex = self.exists
            self.exists = True

    def create(self):
        self.vertex = self.create_vertex(
            self.term_label,
            'term',
            self.term
        )

    def get_relationships(self):
        search_string = """
            MATCH (t:`Unique Term` {term:"%s"})-[rel:`IS_ASSOCIATED_WITH`]-()
            RETURN rel
        """ % (self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_documents(self):
        search_string = """
            MATCH (t:`Unique Term` {term:"%s"})<-[:MENTIONS]-(s)
            WITH s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """ % (self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_sentences(self):
        search_string = """
            MATCH (t:`Unique Term` {term:"%s"})<-[:MENTIONS]-(s)
            WITH s
            RETURN DISTINCT s
        """ % (self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_stats(self):
        search_string = """
            MATCH (t:`Unique Term` {term:"%s"})<-[:MENTIONS]-(s)
            WITH s, count(s) as cs
            MATCH (s)-[:CONTAINS]-(d)
            WITH cs, count(d) as cd
            RETURN sum(cs), sum(cd)
        """ % (self.vertex["term"])
        output = self.query(search_string)
        sent_count, doc_count = output[0][0], output[0][1]
        rel_count = len([x for x in self.get_relationships()])
        return sent_count, doc_count, rel_count

    def link_sentence(self, sentence):
        self.create_relationship(sentence.vertex, "MENTIONS", self.vertex)


class Statement(DataModel):
    def __init__(self, statement_id):
        DataModel.__init__(self)
        self.statement_id = statement_id

    def fetch(self):
        self.exists = self.find_vertex(
            self.sentence_label,
            'statement_id',
            self.statement_id
        )
        if self.exists:
            self.create()

    def create(self):
        self.vertex = self.create_vertex(
            self.sentence_label,
            'statement_id',
            self.statement_id
        )

    def _composed_of(self, part):
        self.create_relationship(
            self.vertex,
            "IS_COMPOSED_OF",
            part.vertex
        )

    def link_elements(self, subject, relation, obj):
        new_subject = NounPhrase(subject)
        if not new_subject.exists:
            new_subject.create()
        self._composed_of(new_subject)
        new_object = NounPhrase(obj)
        if not new_object.exists:
            new_object.create()
        new_relation = Relation(relation)
        if not new_relation.exists:
            new_relation.create()
        new_subject.vertex.add_labels("Subject")
        new_object.vertex.add_labels("Object")
        self._composed_of(new_subject)
        self._composed_of(new_object)
        self._composed_of(new_relation)
        self.create_relationship(
            new_subject.vertex,
            "ASSERTION",
            new_relation.vertex
        )
        self.create_relationship(
            new_relation.vertex,
            "RELATED_TO",
            new_object.vertex
        )

    def bulk_map(self, sentence_node, sub, pred, obj):
        print "\nbulk shiiet"
        batch = self.g.neo4j.WriteBatch(self.g.graph)
        noun_index = self.g.graph.get_or_create_index(self.g.neo4j.Node, "noun_phrases")
        predicate_index = self.g.graph.get_or_create_index(self.g.neo4j.Node, "predicate")
        sub_node = batch.get_or_create_in_index(
            self.g.neo4j.Node, noun_index, "noun_phrase", sub, {"noun_phrase": sub}
        )
        obj_node = batch.get_or_create_in_index(
            self.g.neo4j.Node, noun_index, "noun_phrase", obj, {"noun_phrase": obj}
        )
        pred_node = batch.get_or_create_in_index(
            self.g.neo4j.Node, predicate_index, "relation", obj, {"relation": pred}
        )
        result = batch.submit()
        print "result", result


class Relation(DataModel):
    def __init__(self, relation):
        DataModel.__init__(self)
        self.relation = relation

    def fetch(self):
        self.exists = self.find_vertex(
            self.predicate_label,
            'relation',
            self.relation
        )
        if self.exists:
            self.create()

    def create(self):
        self.vertex = self.create_vertex(
             self.predicate_label,
            'relation',
            self.relation
        )


class Policy(Document):
    def __init__(self, policy=None, code=None):
        DataModel.__init__(self)
        self.policy = policy
        self.code = code
        self.link = "%s-%s" % (self.code, self.policy)
        self.label = self.policy_label
        self.fetch()

    def make_policy(self):
        labels = "Policy Agenda"
        properties = {
            "publication": "UK Policy Agendas",
            "title": self.policy,
            "code": self.code
        }
        self.set_node_properties(
            properties,
            labels
        )


class PolicyCategory(Document):
    def __init__(self, category=None, code=None):
        DataModel.__init__(self)
        self.category = category
        self.code = code
        self.link = "%s-%s" % (self.code, self.category)
        self.label = self.category_label
        self.fetch()

    def make_category(self):
        labels = "Policy Category"
        properties = {
            "publication": "UK Policy Agendas",
            "title": self.category,
            "code": self.code
        }
        self.set_node_properties(
            properties,
            labels
        )

    def get_category(self, code):
        search_string = \
            "MATCH (n:`Policy Category`{code:'%s'}) RETURN n" % code
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        if output:
            self.exists = True
            self.vertex = output[0][0]
            return self.vertex
        else:
            return False

    def link_legislation(self, act):
        self.create_relationship(
            act.vertex,
            "RELATED_TO",
            self.vertex
        )

    def link_policy(self, policy):
        self.create_relationship(
            self.vertex,
            "CATEGORY_OF",
            policy.vertex
        )


class ActOfParliament(Document):
    def __init__(self, full_name=None):
        DataModel.__init__(self)
        self.link = full_name
        self.label = self.act_label
        self.fetch()

    def make_act(self, name, description, date):
        labels = "Act of Parliament"
        properties = {
            "publication": "UK Parliament",
            "title": name,
            "content": description
        }
        self.set_node_properties(
            properties,
            labels
        )
        self.set_assent_date(date)


class DebateInParliament(DataModel):
    def __init__(self, debate_id):
        DataModel.__init__(self)
        self.debate_id = debate_id
        self.fetch()

    def fetch(self):
        self.exists = self.find_vertex(
            self.debate_label,
            'debate_id',
            self.debate_id
        )
        if self.exists:
            self.vertex = self.exists
            self.exists = True

    def create(self):
        self.vertex = self.create_vertex(
            self.debate_label,
            'debate_id',
            self.debate_id
        )

    def link_debate(self, debate):
        self.create_relationship(
            debate.vertex,
            "RELATED_TO",
            self.vertex
        )

    def link_argument(self, argument):
        self.create_relationship(
            self.vertex,
            "HAS_COMMENT",
            argument.vertex
        )


class DebateArgument(Document):
    def __init__(self, link, topic, content):
        DataModel.__init__(self)
        self.speaker = None
        self.link = link
        self.topic = topic
        self.content = content
        self.label = self.document_label
        self.fetch()

    def make_argument(self):
        labels = "Argument"
        if self.speaker:
            title = "%s - %s" % (self.speaker, self.topic)
        else:
            title = self.topic
        properties = {
            "publication": "They Work for You",
            "title": title,
            "content": self.content
        }
        self.set_node_properties(
            properties,
            labels
        )

    def link_speaker(self, speaker):
        debate_mp = MemberOfParliament(speaker)
        if not debate_mp.exists:
            debate_mp.create()
            debate_mp.update_mp_details()
        self.create_relationship(
            debate_mp.vertex,
            "STATED",
            self.vertex
        )
