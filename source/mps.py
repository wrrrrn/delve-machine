from source import CacheInterface
from time import sleep


class GetMPs(CacheInterface):
    def __init__(self):
        CacheInterface.__init__(self)
        self.text = self.speech_tools.TextHandler()
        self.cache = self.cache_models.Representatives()
        self.mps = self.hansard.get_mps()

    def fetch(self):
        for mp in self.mps:
            self._print_out("MP", mp["name"])
            self._print_out("Party", mp["party"])
            self._print_out("person_id", mp["person_id"])
            node = {
                "full_name": mp["name"],
                "twfy_id": mp["person_id"],
                "party": mp["party"]
            }
            print "\n"
            details = self.hansard.get_mp_details(mp["person_id"])
            if details:
                node["first_name"] = details[0]["first_name"]
                node["last_name"] = details[0]["last_name"]
                node["number_of_terms"] = len(details)
            terms = []
            for entry in details:
                term = {
                    "party": entry["party"],
                    "constituency": entry['constituency'],
                    "left_house": entry["left_house"],
                    "entered_house": entry["entered_house"],
                    "left_reason": entry["left_reason"]
                }
                if "office" in entry:
                    offices = self._get_office(entry["office"])
                    if len(offices) > 0:
                        term["offices_held"] = offices
                terms.append(term)
            node["terms"] = terms
            self._report(node)
            print self.cache.write(node)
            print "---"

    def _get_office(self, positions):
        offices = []
        if len(positions) > 1:
            for position in positions:
                office = {}
                if position["dept"]:
                    office = {"department": position["dept"]}
                if position["position"]:
                    office = {"position": position["position"]}
                offices.append(office)
        else:
            office = {}
            if positions[0]["dept"]:
                office = {"department": positions[0]["dept"]}
            if positions[0]["position"]:
                office = {"position": positions[0]["position"]}
            offices.append(office)
        if len(offices) == 0:
            return None
        else:
            return offices

    def _report(self, node):
        for x in node:
                if x == "terms":
                    for term in node["terms"]:
                        print "-"
                        for y in term:
                            if y == "offices_held":
                                offices = term["offices_held"]
                                if len(offices) > 1 and offices != "none":
                                    for office in offices:
                                        for z in office:
                                            self._print_out(z, office[z])
                                else:
                                    if not offices == "none":
                                        for z in offices[0]:
                                            self._print_out(z, offices[0][z])
                            else:
                                self._print_out(y, term[y])
                else:
                    self._print_out(x, node[x])

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)