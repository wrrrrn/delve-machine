from source import ImportInterface


class ImportCodebook(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.verbose = True
        self.build_semantic_graph = False
        self.codebook_csv = \
            'source/input/policyagenda_UK_Topics_Codebook-main.csv'

    def import_codebook(self):
        self.csv_handler.open(self.codebook_csv)
        data = self.csv_handler.all_rows
        for row in data:
            major_code = row[0]
            policy = row[1]
            code = row[2]
            category = row[3]
            description = row[4]
            if self.verbose:
                print '\nmajor_code: %s\npolicy: %s\ncode: %s - %s\n' % (
                    major_code,
                    policy,
                    code,
                    category
                )
            new_policy = self._create_policy(policy, major_code)
            category_name = self._parse_category_name(policy, category)
            new_category = self._create_category(category_name, code, description)
            new_category.link_policy(new_policy)
            self.parser.parse_document(new_policy, policy, map_statements=False)
            self.parser.parse_document(new_category, description, map_statements=False)
        if self.verbose:
            print '---\n'

    def _create_policy(self, policy, code):
        new_policy = self.data_models.Policy(policy, code)
        if not new_policy.exists:
            new_policy.create()
        new_policy.make_policy()
        new_policy.update_content(policy)
        return new_policy

    def _create_category(self, category, code, description):
        new_category = self.data_models.PolicyCategory(category, code)
        if not new_category.exists:
            new_category.create()
        new_category.make_category()
        new_category.update_content(description)
        return new_category

    def _parse_category_name(self, policy, text):
        if "combinations of multiple subtopics" in text.lower():
            category = "General %s" % policy
        elif "other." in text.lower():
            category = "Other %s" % policy
        elif text[-1] == ".":
            category = text[:-1]
        else:
            category = text
        return category


