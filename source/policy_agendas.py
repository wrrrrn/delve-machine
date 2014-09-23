from source import CacheInterface


class PolicyResearch(CacheInterface):
    def __init__(self):
        CacheInterface.__init__(self)
        self.codebook_csv = \
            'source/input/policyagenda_UK_Topics_Codebook-main.csv'
        self.cache = self.cache_models.PolicyAgenda()

    def import_policies(self):
        self.csv_handler.open(self.codebook_csv)
        data = self.csv_handler.all_rows
        for row in data:
            policy = {
                "major_code": row[0],
                "policy": row[1],
                "code": row[2],
                "category": row[3],
                "description": row[4]
            }
            self.cache.write(policy)