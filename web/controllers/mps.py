from data_models import core, models


class MpAggregateController:
    def __init__(self):
        self.positions_model = models.GovernmentPosition()
        self.data_model = core.DataModel()
        self.government = []
        self.opposition = []
        self._set_properties()

    def government_positions(self):
        for mp, weight in self.government:
            print "gov:", mp
            yield mp, weight

    def opposition_positions(self):
        for mp, weight in self.opposition:
            print "opp:", mp
            yield mp, weight

    def _set_properties(self):
        for p in self.positions_model.get_current_positions():
            shadow, government = False, False
            mp, party, image, positions, weight = p[0], p[1], p[2], p[3], p[4]
            mp_detail = {
                "name": mp,
                "party": party,
                "image": image,
                "positions": positions
            }
            for pos in positions:
                if "Shadow" in pos or party == "Labour":
                    shadow = True
                elif party in ['Liberal Democrat', 'Conservative']:
                    government = True
            if shadow:
                self.opposition.append((mp_detail, weight))
            if government:
                self.government.append((mp_detail, weight))

    def _get_departments(self, mp):
        search_query = u"""
            MATCH (mp:`Noun Phrase` {{noun_phrase:"{0}"}}) with mp
            MATCH (mp)-[:REPRESENTATIVE_FOR]-(t)
            where t.left_office = "still_in_office" with mp, t
            MATCH (t)-[:SERVED_IN]-(g:`Government Department`)
            RETURN collect(g.noun_phrase) as dept
        """.format(mp)
        result = self.data_model.query(search_query)
        return result[0]