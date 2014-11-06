from data_models import models


class MpsApi:
    def __init__(self):
        self.mps = models.MembersOfParliament()
        self.all = []
        self.government_members = []
        self.opposition_members = []

    def get_all(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.all

    def get_government(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.government_members

    def get_opposition(self, page_size=20, skip_to=0):
        self._fetch(page_size, skip_to)
        return self.opposition_members

    def _fetch(self, page_size=20, skip_to=0):
        result = self.mps.get_all_mps(page_size, skip_to)
        for mp in result:
            shadow, government = False, False
            weight = {"weight": mp[3]}
            mp, party, image = mp[0], mp[1], mp[2]
            mp_detail = models.MemberOfParliament(mp)
            positions = mp_detail.positions
            departments = mp_detail.departments
            aggregate_detail = {
                "name": mp,
                "party": party,
                "image": image,
                "positions": positions,
                "departments": departments
            }
            self.all.append((aggregate_detail, weight))
            for pos in positions:
                if "Shadow" in pos or party == "Labour":
                    shadow = True
                elif party in ['Liberal Democrat', 'Conservative']:
                    government = True
            if shadow:
                self.opposition_members.append((aggregate_detail, weight))
            if government:
                self.government_members.append((aggregate_detail, weight))
