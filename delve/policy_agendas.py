from delve import ImportInterface


class ImportPolicies(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.PolicyAgenda()

    def delve(self):
        for doc in self.cache.fetch_all():
            self._import(doc)

    def _import(self, node):
        new_policy = self._create_policy(node["policy"], node["major_code"])
        self.parser.parse_document(
            new_policy,
            node["policy"],
            map_statements=False
        )
        category_name = self._parse_category(node["policy"], node["category"])
        new_category = self._create_category(
            category_name,
            node["code"],
            node["description"]
        )
        new_category.link_policy(new_policy)
        self.parser.parse_document(
            new_category,
            node["description"],
            map_statements=False
        )

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

    def _parse_category(self, policy, text):
        if "combinations of multiple subtopics" in text.lower():
            category = "General %s" % policy
        elif "other." in text.lower():
            category = "Other %s" % policy
        elif text[-1] == ".":
            category = text[:-1]
        else:
            category = text
        return category