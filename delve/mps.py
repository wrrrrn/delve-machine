from delve import ImportInterface


class ImportMPs(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Politicians()

    def delve(self):
        for doc in self.cache.fetch_all():
            self._import(doc)

    def _import(self, node):
        mp = self.import_mp(node)
        if "terms" in node:
            self.import_terms(mp, node["terms"])

    def import_mp(self, node):
        print "\n.................."
        print node["full_name"], "x", node["number_of_terms"]
        print node["party"]
        print ".................."
        #print node["twfy_id"]
        return self._create_mp(node)

    def _create_mp(self, mp):
        new_mp = self.data_models.MemberOfParliament(mp["full_name"])
        mp_details = {
            "first_name": mp["first_name"],
            "last_name": mp["last_name"],
            "party": mp["party"],
            "twfy_id": mp["twfy_id"],
            "number_of_terms": mp["number_of_terms"]
        }
        if mp["guardian_url"]:
            mp_details["guardian_url"] = mp["guardian_url"]
        if mp["publicwhip_url"]:
            mp_details["publicwhip_url"] = mp["publicwhip_url"]
            mp_details["publicwhip_id"] = mp["publicwhip_id"]
        if not new_mp.exists:
            new_mp.create()
        new_mp.update_mp_details(mp_details)
        new_mp.link_party(mp["party"])
        return new_mp

    def import_terms(self, mp, terms):
        for term in terms:
            print term["constituency"], term["party"]
            print term["entered_house"], "to", term["left_house"]
            print term["left_reason"]
            new_term = self._create_term(term)
            mp.link_session(new_term)
            if "offices_held" in term:
                self._create_offices(new_term, term["offices_held"])
            print "-"

    def _create_term(self, term):
        session = u"{0} {1} {2} to {3}".format(
            term["constituency"],
            term["party"],
            term["entered_house"],
            term["left_house"]
        )
        new_term = self.data_models.TermInParliament(session)
        if not new_term.exists:
            new_term.create()
        term = {
            "party": term["party"],
            "constituency": term['constituency'],
            "left_house": term["left_house"],
            "entered_house": term["entered_house"],
            "left_reason": term["left_reason"]
        }
        new_term.update_details(term)
        return new_term

    def _create_offices(self, term, offices):
        print "*"
        if len(offices) > 1 and offices != "none":
            for office in offices:
                if "department" in office:
                    self._create_office(
                        term,
                        "department",
                        office["department"]
                    )
                if "position" in office:
                    self._create_office(
                        term,
                        "position",
                        office["position"]
                    )
        else:
            if not offices == "none":
                if "department" in offices[0]:
                    self._create_office(
                        term,
                        "department",
                        offices[0]["department"]
                    )
                if "position" in offices[0]:
                    self._create_office(
                        term,
                        "position",
                        offices[0]["position"]
                    )

    def _create_office(self, term, create_as, office):
        print office
        if create_as == "department":
            new_office = self.data_models.GovernmentDepartment(office)
        elif create_as == "position":
            new_office = self.data_models.GovernmentPosition(office)
        if not new_office.exists:
            new_office.create()
        new_office.update_details()
        term.link_position(new_office)

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)