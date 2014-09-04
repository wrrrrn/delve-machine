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

    def import_mp_debates(self):
        for mp in self.mps:
            self._get_debates(mp)

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
        new_mp = self.data_models.MemberOfParliament(mp["full_name"])
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

    def _get_debates(self, person):
        mp_debates = self.hansard.get_mp_debates("commons", person['person_id'])
        print "MP Debates Count:", mp_debates["info"]["total_results"]
        if mp_debates:
            for result in mp_debates["rows"]:
                start, sub, comment = self.hansard.get_debate(result["gid"])
                if sub:
                    topic, sub_cat, full_debate = \
                        self.hansard.get_full_debate(sub["debate_id"])
                    print topic
                    new_topic = self._create_debate(topic)
                    new_subcat = self._create_debate(sub_cat)
                    new_topic.link_debate(new_subcat)
                    self._interate_debate(new_subcat, full_debate)
                else:
                    print start
                    if start["content_count"] > 0:
                        new_topic = self._create_debate(start)
                        topic, sub_cat, full_debate = \
                            self.hansard.get_full_debate(start["debate_id"])
                        self._interate_debate(new_topic, full_debate)
                print "-"

    def _interate_debate(self, debate, arguments):
        for entry in arguments:
            scrubbed_text = self.text.parse_raw_html(entry["body"])
            topic = debate.vertex["topic"]
            argument = self._create_argument(entry["gid"], topic, scrubbed_text)
            debate.link_argument(argument)
            self.parser.parse_document(argument, scrubbed_text, map_statements=False)
            if "speaker" in entry and "person_id" in entry["speaker"]:
                name = "%s %s" % (
                    entry["speaker"]["first_name"],
                    entry["speaker"]["last_name"]
                )
                argument.link_speaker(name)
            argument.make_argument()
            print "Comment:\n", scrubbed_text[:200]
            print "\n"

    def _create_debate(self, topic):
        new_debate = self.data_models.DebateInParliament(topic["debate_id"])
        if "body" in topic:
            new_properties = {"topic": topic["body"], "date": topic["date"]}
        else:
            new_properties = {"topic": topic["topic"], "date": topic["date"]}
        if not new_debate.exists:
            new_debate.create()
            new_debate.set_node_properties(properties=new_properties)
        return new_debate

    def _create_argument(self, link, topic, text):
        argument = self.data_models.DebateArgument(link, topic, text)
        if not argument.exists:
            argument.create()
        return argument

    def _print_all(self, dic):
        for k in dic:
            self._print_out(k, dic[k])
        print "\n"

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)