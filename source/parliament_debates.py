from source import CacheInterface


class Parliament(CacheInterface):
    def __init__(self, verbose=True):
        CacheInterface.__init__(self)
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
                result = self.hansard.get_debate(result["gid"])
                if result:
                    start, sub, comment = result[0], result[1], result[2]
                    if sub:
                        topic, sub_cat, full_debate = \
                            self.hansard.get_full_debate(sub["debate_id"])
                        print "TOPIC:", topic["topic"], "\n"
                        new_topic = self._create_debate(topic)
                        if new_topic:
                            new_subcat = self._create_debate(sub_cat)
                            if new_subcat:
                                new_topic.link_debate(new_subcat)
                                self._interate_debate(new_subcat, full_debate)
                        else:
                            print "IMPORTED"
                    else:
                        print "START:", start, "\n"
                        if start["content_count"] > 0:
                            new_topic = self._create_debate(start)
                            if new_topic:
                                topic, sub_cat, full_debate = \
                                    self.hansard.get_full_debate(start["debate_id"])
                                self._interate_debate(new_topic, full_debate)
                            else:
                                print "IMPORTED"
                print "-"

    def _interate_debate(self, debate, arguments):
        previous_argument = None
        for entry in arguments:
            #print entry
            scrubbed_text = self.text.parse_raw_html(entry["body"])
            topic = debate.vertex["topic"]
            new_argument = self._create_argument(entry["gid"], topic, scrubbed_text)
            debate.link_argument(new_argument)
            if "speaker" in entry and "person_id" in entry["speaker"]:
                name = "%s %s" % (
                    entry["speaker"]["first_name"],
                    entry["speaker"]["last_name"]
                )
                new_argument.link_speaker(name)
                print "\n\n%s Comment on %s:\n" % (name, topic), scrubbed_text, "\n__\n"
            new_argument.make_argument()
            self.parser.parse_document(new_argument, scrubbed_text, map_statements=False)
            new_argument.link_previous(previous_argument)
            previous_argument = new_argument

    def _create_debate(self, topic):
        new_debate = self.data_models.DebateInParliament(topic["debate_id"])
        if "body" in topic:
            topic, date = topic["body"], topic["date"]
        else:
            topic, date = topic["topic"], topic["date"]
        if not new_debate.exists:
            new_debate.create()
            new_debate.make_debate(topic, date)
            return new_debate
        else:
            return None

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