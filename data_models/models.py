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
            u'MATCH (n:`Sentence` {sentence_id:"{0}"})-[]->(x:`Statement`) ' \
            u"return x".format(self.sentence_id)
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        for result in output:
            yield result[0]

    def get_statement_parts(self, part_type):
        search_string = \
            u'MATCH (n:`Sentence` {sentence_id:"{0}"})-[]->(x:`Statement`)-[]->(y:`{1}`) ' \
            u"return  y ".format(self.sentence_id, part_type)
        search_test = self.g.neo4j.CypherQuery(self.g.graph, search_string)
        output = search_test.execute()
        for result in output:
            yield result[0]


class NounPhrase(DataModel):
    def __init__(self, noun_phrase=False):
        DataModel.__init__(self)
        self.noun_phrase = noun_phrase
        self.label = self.noun_label
        self._incoming = ["MENTIONS", "MEMBER_OF", "IN_POSITION"]
        self._outgoing = [
            "IS_ASSOCIATED_WITH", "STATED", "MEMBER_OF", "IN_POSITION"
        ]
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
        search_string = u"""
            MATCH (n:`Noun Phrase` {{noun_phrase:"{0}"}})-[rel:`{1}`]->()
            RETURN rel
        """.format(self.vertex["noun_phrase"], relationship)
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_documents(self):
        search_string = u"""
            MATCH (np:`Noun Phrase` {{noun_phrase:"{0}"}})<-[:MENTIONS]-(s)
            WITH s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_associated(self):
        search_string = u"""
            MATCH (np:`Noun Phrase` {{noun_phrase:"{0}"}})-[:IS_ASSOCIATED_WITH]-(x)
            WITH x
            MATCH (x)-[]-(y)
            RETURN x, count(y) as weight
            ORDER BY weight DESC
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0], result[1]

    def get_associated_documents(self):
        search_string = u"""
            MATCH (np:`Noun Phrase` {{noun_phrase:"{0}"}})-[:IS_ASSOCIATED_WITH]-(t)
            WITH t
            MATCH (t)<-[:MENTIONS]-(s) with s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """.format(self.vertex["noun_phrase"])
        print search_string
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_statements(self):
        search_string = u"""
            MATCH (`Member of Parliament`  {{noun_phrase:"{0}"}})-[:STATED]->(s)
            RETURN DISTINCT s
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_positions(self):
        search_string = u"""
            MATCH (`Member of Parliament`  {{noun_phrase:"{0}"}})-
            [:REPRESENTATIVE_FOR]->()-[:SERVED_IN]-(y)
            RETURN DISTINCT y
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_sentences(self):
        search_string = u"""
            MATCH (np:`Noun Phrase` {{noun_phrase:"{0}"}})<-[:MENTIONS]-(s)
            RETURN DISTINCT s
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_terms_in_parliament(self):
        search_string = u"""
            MATCH (np:`Noun Phrase` {{noun_phrase:"{0}"}})-[:REPRESENTATIVE_FOR]->(t)
            RETURN DISTINCT t
        """.format(self.vertex["noun_phrase"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_outgoing(self):
        output = []
        for rel in self._outgoing:
            search_string = u"""
                MATCH (n:`Noun Phrase` {{noun_phrase:'{0}'}})-[:{1}]->(x)
                RETURN DISTINCT x
            """.format(self.vertex["noun_phrase"], rel)
            search_result = self.query(search_string)
            for r in search_result:
                output.append((rel, r[0]))
        for result in output:
            yield result

    def get_incoming(self):
        output = []
        for rel in self._incoming:
            search_string = u"""
                MATCH (n:`Noun Phrase` {{noun_phrase:'{0}'}})<-[:{1}]-(x)
                RETURN DISTINCT x
            """.format(self.vertex["noun_phrase"], rel)
            search_result = self.query(search_string)
            for r in search_result:
                output.append((rel, r[0]))
        for result in output:
            yield result

    def get_stats(self):
        search_string = u"""
            MATCH (t:`Noun Phrase` {{noun_phrase:"{0}"}})<-[:MENTIONS]-(s)
            WITH s, count(s) as cs
            MATCH (s)-[:CONTAINS]-(d)
            WITH cs, count(d) as cd
            RETURN sum(cs), sum(cd)
        """.format(self.vertex["noun_phrase"])
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
        labels = ["Named Entity", "Member of Parliament", "Parliamentary Matters"]
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
        labels = ["Noun Phrase", "Named Entity", "Political Party"]
        if not party.exists:
            party.create()
        party.set_node_properties(labels=labels)
        self.create_relationship(self.vertex, "MEMBER_OF", party.vertex)

    def link_session(self, term):
        self.create_relationship(self.vertex, "REPRESENTATIVE_FOR", term.vertex)


class TermInParliament(NounPhrase):
    def __init__(self, session):
        NounPhrase.__init__(self)
        self.noun_phrase = session
        self.label = self.noun_label
        self.fetch()

    def update_details(self, properties=None):
        labels = ["Term in Parliament", "Parliamentary Matters"]
        self.set_node_properties(
            properties,
            labels
        )
        if properties["entered_house"]:
            self.set_date(properties["entered_house"], "ENTERED_HOUSE")
        if properties["left_reason"]:
            self.set_date(properties["left_house"], "LEFT_HOUSE")

    def link_position(self, position):
        self.create_relationship(self.vertex, "SERVED_IN", position.vertex)


class GovernmentDepartment(NounPhrase):
    def __init__(self, name):
        NounPhrase.__init__(self)
        self.noun_phrase = name
        self.label = self.noun_label
        self.fetch()

    def update_details(self, details=None):
        labels = ["Named Entity", "Government Department", "Parliamentary Matters"]
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
        labels = ["Named Entity", "Government Position", "Parliamentary Matters"]
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
        search_string = u"""
            MATCH (t:`Unique Term` {term:"{0}"})-[rel:`IS_ASSOCIATED_WITH`]-()
            RETURN rel
        """.format(self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_documents(self):
        search_string = u"""
            MATCH (t:`Unique Term` {term:"{0}"})<-[:MENTIONS]-(s)
            WITH s
            MATCH (s)-[:CONTAINS]-(d)
            RETURN DISTINCT d
        """.format(self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_sentences(self):
        search_string = u"""
            MATCH (t:`Unique Term` {term:"{0}"})<-[:MENTIONS]-(s)
            WITH s
            RETURN DISTINCT s
        """.format(self.vertex["term"])
        output = self.query(search_string)
        for result in output:
            yield result[0]

    def get_stats(self):
        search_string = u"""
            MATCH (t:`Unique Term` {term:"{0}"})<-[:MENTIONS]-(s)
            WITH s, count(s) as cs
            MATCH (s)-[:CONTAINS]-(d)
            WITH cs, count(d) as cd
            RETURN sum(cs), sum(cd)
        """.format(self.vertex["term"])
        output = self.query(search_string)
        sent_count, doc_count = output[0][0], output[0][1]
        rel_count = len([x for x in self.get_relationships()])
        return sent_count, doc_count, rel_count

    def link_sentence(self, sentence):
        self.create_relationship(sentence.vertex, "MENTIONS", self.vertex)


class Policy(Document):
    def __init__(self, policy=None, code=None):
        DataModel.__init__(self)
        self.policy = policy
        self.code = code
        self.link = u"{0}-{1}".format(self.code, self.policy)
        self.label = self.policy_label
        self.fetch()

    def make_policy(self):
        labels = ["Document"]
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
        self.link = u"{0}-{1}".format(self.code, self.category)
        self.label = self.category_label
        self.fetch()

    def make_category(self):
        labels = ["Document"]
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
            u"MATCH (n:`Policy Category`{code:'{0}'}) RETURN n".format(code)
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
        labels = ["Parliamentary Matters", "Document"]
        properties = {
            "publication": "UK Parliament",
            "title": name,
            "content": description
        }
        self.set_node_properties(
            properties,
            labels
        )
        self.set_date(date, "RECEIVED_ROYAL_ASSENT")


class DebateInParliament(Document):
    def __init__(self, link):
        DataModel.__init__(self)
        self.link = link
        self.label = self.debate_label
        self.fetch()

    def make_debate(self, topic, date):
        labels = ["Parliamentary Matters", "Document"]
        properties = {
            "publication": "They Work for You",
            "topic": topic,
        }
        self.set_node_properties(
            properties,
            labels
        )
        self.set_date(date, "DEBATED_ON")

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
        self.label = self.argument_label
        self.fetch()

    def make_argument(self):
        labels = ["Parliamentary Matters", "Document"]
        if self.speaker:
            title = u"{0} - {1}".format(self.topic, self.speaker)
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
        self.speaker = speaker
        debate_mp = MemberOfParliament(speaker)
        if not debate_mp.exists:
            debate_mp.create()
            debate_mp.update_mp_details()
        self.create_relationship(
            debate_mp.vertex,
            "STATED",
            self.vertex
        )

    def link_previous(self, argument):
        if argument:
            self.create_relationship(
                self.vertex,
                "RESPONSE_TO",
                argument.vertex
            )


class VoteinParliament(Document):
    def __init__(self, vote_number, topic=None):
        DataModel.__init__(self)
        self.bill = topic
        self.vote_number = vote_number
        self.link = u"{0} - {1}".format(vote_number, self.bill)
        self.label = self.vote_label
        self.fetch()

    def make_vote(self, date):
        labels = ["Parliamentary Matters", "Document"]
        properties = {
            "publication": "Public Whip",
            "bill": self.bill
        }
        self.set_node_properties(
            properties,
            labels
        )
        self.set_date(date, "VOTED_ON")

    def link_debate(self, vote_category):
        self.create_relationship(
            self.vertex,
            "VOTING_CATEGORY",
            vote_category.vertex
        )


class VoteCategory(Document):
    def __init__(self, bill, category):
        DataModel.__init__(self)
        self.bill = bill
        self.vote_category = category
        self.label = self.votecategory_label
        self.link = u"{0} - {1}".format(bill, category)
        self.fetch()

    def make_category(self):
        labels = ["Parliamentary Matters"]
        properties = {
            "publication": "Public Whip",
            "category": self.link
        }
        self.set_node_properties(
            properties,
            labels
        )

    def link_vote(self, mp):
        self.create_relationship(
            self.vertex,
            "VOTE_CAST",
            mp.vertex
        )
