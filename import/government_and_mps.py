from interfaces import theyworkforyou
import json


class ImportGovernment:
    def __init__(self, csv_handler, database, models, speech_tools, verbose=True):
        self.verbose = verbose
        self.csv_handler = csv_handler
        self.government_csv = 'import/input/Government Departments - Members.csv'
        self.opposition_csv = 'import/input/Opposition Departments - Members.csv'
        self.g = database
        self.core_model = models.DataModel(self.g)
        self.twfy = theyworkforyou.TWFY('D4kApuGX4PE9G8NvmkEKRTmV')
        self.speech_tools = speech_tools.TextHandler()

    def import_all_departments(self):
        self.import_departments(self.government_csv)
        self.import_departments(self.opposition_csv)

    def import_departments(self, csv):
        if self.verbose:
            print 'Importing Government departments'
        self.csv_handler.open(csv)
        data = self.csv_handler.all_rows
        for row in data:
            name = row[1]
            department = row[0]
            if 'Edward' in name:
                new_name = ["Ed" if x == 'Edward' else x for x in name.split(" ")]
                name = ' '.join(new_name).strip()
            if self.verbose:
                print '%s MEMBER_OF %s' % (name, department)
            self.add_government_relationship(
                name,
                department
            )

    def add_government_relationship(self, name, department):
        mp_vertex = self.core_model.get_or_create(
            "name",
            name,
            self.core_model.named_reference
        )
        mp_vertex.add_labels("Politician", "Member of Parliament")
        department_model = self.core_model
        department_vertex = department_model.get_or_create(
            "name",
            department,
            self.core_model.named_reference
        )
        department_vertex.add_labels("Government Department")
        self.core_model.create_relationship(
            mp_vertex,
            "MEMBER_OF",
            department_vertex
        )
        self.link_department_to_semantics(department_model, department)

    def link_department_to_semantics(self, model, words):
        department_words = self.speech_tools.get_words(
            words,
            with_punctuation=False,
            remove_stopwords=True
        )
        model.link_nodes(
            department_words,
            model.terms_reference,
            "term",
            "RELATED_TO",
            "incoming"
        )

    def import_mp_details(self):
        if self.verbose:
            print 'Importing MP Details'
        self.mps = json.loads(self.twfy.api.getMPs(output='js'), 'iso-8859-1')
        for mp in self.mps:
            party = mp['party']
            name = mp['name']
            if 'Edward' in name:
                new_name = ["Ed" if x == 'Edward' else x for x in name.split(" ")]
                name = ' '.join(new_name).strip()
            constituency = mp['constituency']
            if self.verbose:
                try:
                    print name.decode('unicode-escape'),\
                        party.decode('unicode-escape'),\
                        constituency.decode('unicode-escape')
                except UnicodeEncodeError:
                    pass
            self.add_party_relationship(
                name,
                party
            )
            self.add_constituency_relationship(
                name,
                constituency
            )
            # print name, party, constituency

    def add_party_relationship(self, name, party):
        party_vertex = self.core_model.get_or_create(
            "name",
            party,
            self.core_model.named_reference
        )
        party_vertex.add_labels("Political Party")
        mp_vertex = self.core_model.get_or_create(
            "name",
            name,
            self.core_model.named_reference
        )
        mp_vertex.vertex["political party"] = party
        mp_vertex.add_labels('Politician')
        self.core_model.create_relationship(
            mp_vertex,
            "MEMBER_OF",
            party_vertex
        )

    def add_constituency_relationship(self, name, constituency):
        mp_vertex = self.core_model.get_or_create(
            "name",
            name,
            self.core_model.named_reference
        )
        const_vertex = self.core_model.get_or_create(
            "name",
            constituency,
            self.core_model.named_reference
        )
        const_vertex.add_labels("Constituency")
        self.core_model.create_relationship(
            mp_vertex,
            "REPRESENTS",
            const_vertex
        )


# import_mp_details()