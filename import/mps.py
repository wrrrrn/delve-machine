from data_imports import ImportInterface
from time import sleep


class ImportMPs(ImportInterface):
    def __init__(self, verbose=True):
        ImportInterface.__init__(self)
        self.verbose = verbose
        self.text = self.speech_tools.TextHandler()
        self.mps = self.hansard.get_mps()
        print '\n\nMembers of Parliament [count:%s]' % len(self.mps)

    def import_mp_details(self):
        for mp in self.mps:
            self._print_out("MP", mp["name"])
            self._print_out("Party", mp["party"])
            self._print_out("person_id", mp["person_id"])
            print "\n"
            self._get_mp(mp['person_id'])
            sleep(0.25)
            print "---"

    def _get_mp(self, person_id):
        new_mp = None
        mp_detail = self.hansard.get_mp_details(person_id)
        if mp_detail:
            new_mp = self._create_mp(mp_detail[0], len(mp_detail))
            if "office" in mp_detail[0]:
                self._link_office_detail(new_mp, mp_detail[0]["office"])
        return new_mp

    def _create_mp(self, mp, terms):
        mp_details = {
            "first_name": mp["first_name"],
            "last_name": mp["last_name"],
            "full_name": mp["full_name"],
            "party": mp["party"],
            "constituency": mp['constituency'],
            "left_house": mp["left_house"],
            "entered_house": mp["entered_house"],
            "number_of_terms": terms,
            "left_reason": mp["left_reason"]
        }
        for x in mp_details:
            self._print_out(x, mp_details[x])
        name = mp["full_name"].encode('ascii', 'ignore')
        new_mp = self.data_models.MemberOfParliament(name)
        if not new_mp.exists:
            new_mp.create()
        new_mp.update_mp_details(mp_details)
        new_mp.link_party(mp["party"])
        return new_mp

    def _link_office_detail(self, mp, positions):
        if len(positions) > 1:
            for position in positions:
                self._create_department(mp, position["dept"])
                self._create_position(mp, position["position"])
        else:
            self._create_department(mp, positions[0]["dept"])
            self._create_position(mp, positions[0]["position"])

    def _create_department(self, mp, department):
        if len(department) > 2:
            new_department = self.data_models.GovernmentDepartment(department)
            if not new_department.exists:
                new_department.create()
            new_department.update_details()
            mp.link_department(new_department)
            self._print_out("*department", department)

    def _create_position(self, mp, position):
        if len(position) > 2:
            new_position = self.data_models.GovernmentPosition(position)
            if not new_position.exists:
                new_position.create()
            new_position.update_details()
            mp.link_position(new_position)
            self._print_out("*position", position)

    def _print_all(self, dic):
        for k in dic:
            self._print_out(k, dic[k])
        print "\n"

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)