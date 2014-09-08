from data_imports import ImportInterface


class ImportActsOfParliament(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.acts_csv = \
            'data_imports/input/policyagenda_acts_test.csv'
            #'data_imports/input/policyagenda_acts1911-2008.csv'
        self.text = self.speech_tools.TextHandler()

    def import_acts(self):
        self.csv_handler.open(self.acts_csv)
        data = self.csv_handler.all_rows
        for row in data:
            royal_assent = row[2]
            short_title = row[4].encode('ascii', 'ignore')
            long_title = row[5].encode('ascii', 'ignore')
            major_topic = row[6]
            sub_topic = row[7]
            print '%s\nassent date: %s - major code: %s - sub code: %s\n' % (
                short_title,
                royal_assent,
                major_topic,
                sub_topic
            )
            new_act = self._create_act(short_title, long_title, royal_assent)
            self.parser.parse_document(new_act, long_title, map_statements=False)
            category = self._get_related_category(sub_topic)
            if category:
                category.link_legislation(new_act)
            print '---\n'

    def _create_act(self, full_name, description, date):
        act_name = full_name.split(" ")
        act_name.pop()
        if len(act_name) > 1 and act_name[-1] == 'c.':
            act_name.pop()
        act_name = ' '.join(act_name).strip()
        new_act = self.data_models.ActOfParliament(full_name)
        if not new_act.exists:
            new_act.create()
            new_act.make_act(act_name, description, date)
        return new_act

    def _get_related_category(self, code):
        category = self.data_models.PolicyCategory()
        category.get_category(code)
        if category.exists:
            print "*", category.vertex['title']
            return category
        else:
            print "* category code not found: ", code
            return None
