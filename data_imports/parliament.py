from data_imports import ImportInterface
from time import sleep


class Parliament(ImportInterface):
    def __init__(self, verbose=True):
        ImportInterface.__init__(self)
        self.verbose = verbose
        self.text = self.speech_tools.TextHandler()
        self.mps = self.hansard.get_mps()

    def import_debates(self):
        for mp in self.mps:
            self._get_debates(mp)

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