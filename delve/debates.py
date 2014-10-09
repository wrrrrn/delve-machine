from delve import ImportInterface


class ImportDebates(ImportInterface):
    def __init__(self):
        ImportInterface.__init__(self)
        self.cache = self.cache_models.Debates()

    def delve(self):
        for doc in self.cache.fetch_all(return_list=True):
            self._report(doc)
            self._import(doc)

    def _import(self, node):
        new_debate = self._create_debate(node)
        if "sub_topics" in node:
            for sub in node["sub_topics"]:
                new_sub = self._create_debate(sub)
                new_debate.link_debate(new_sub)
                self._iterate_arguments(new_sub, sub["arguments"])
        else:
            self._iterate_arguments(new_debate, node["arguments"])

    def _create_debate(self, debate):
        new = self.data_models.DebateInParliament(debate["debate_id"])
        if not new.exists:
            new.create()
            new.make_debate(debate["topic"], debate["date"])
        return new

    def _iterate_arguments(self, debate_node, arguments):
        previous_argument = None
        for entry in arguments:
            text = entry["text"]
            topic = debate_node.vertex["topic"]
            summary = self.summerizer.summarize(
                topic,
                text
            )
            summary = ' '.join(summary)
            new_argument = self._create_argument(
                debate_node.vertex["debate_id"],
                topic,
                text,
                summary
            )
            debate_node.link_argument(new_argument)
            if "speaker" in entry:
                name = entry["speaker"]["name"]
                new_argument.link_speaker(name)
                print "\n\n%s Comment on %s:" % (name, topic)
                print text, "\n__\n"
            new_argument.make_argument()
            self.parser.parse_document(new_argument, text, map_statements=False)
            new_argument.link_previous(previous_argument)
            previous_argument = new_argument

    def _create_argument(self, link, topic, text, summary):
        arg = self.data_models.DebateArgument(link, topic, text, summary)
        if not arg.exists:
            arg.create()
        return arg

    def _report(self, node):
        print node["topic"]
        self._print_out(node["date"], node["debate_id"])
        if "sub_topics" in node:
            self._print_out("sub topic count:", len(node["sub_topics"]))
            print "..."
            for sub in node["sub_topics"]:
                print sub["topic"]
                self._print_out("argument count:", len(sub["arguments"]))
                print "-"
        elif "arguments" in node:
            print "..."
            self._print_out("argument count:", len(node["arguments"]))
        else:
            print "\n\n\n\n", node, "\n\n\n\n"
        print "\n---"

    def _print_out(self, key, value):
        print "  %-20s%-15s" % (key, value)