from delve import ImportInterface


class ImportActs(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Legislation()

    def delve(self):
        for doc in self.cache.collection.find():
            self._import(doc)

    def _import(self, node):
        royal_assent = node["royal_assent"]
        short_title = node["short_title"]
        long_title = node["long_title"]
        major_topic = node["major_topic"]
        sub_topic = node["sub_topic"]
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
