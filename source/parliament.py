from source import CacheInterface
from time import sleep


class ParliamentData:
    def __init__(self):
        self.acts = ActsOfParliament()
        self.votes = VotesinParliament()
        self.debates = DebatesinParliament()

    def import_acts(self):
        self.acts.import_acts()

    def import_votes(self):
        self.votes.import_votes()

    def import_debates(self):
        self.debates.import_debates()


class ActsOfParliament(CacheInterface):
    def __init__(self):
        CacheInterface.__init__(self)
        self.acts_data = 'source/input/policyagenda_acts1911-2008.csv'
        self.cache = self.cache_models.Legislation()

    def import_acts(self):
        self.csv_handler.open(self.acts_data)
        data = self.csv_handler.all_rows
        for row in data:
            act = {
                "royal_assent": row[2],
                "short_title": row[4],
                "long_title": row[5],
                "major_topic": row[6],
                "sub_topic": row[7]
            }
            print act
            self.cache.write(act)


class VotesinParliament(CacheInterface):
    def __init__(self):
        CacheInterface.__init__(self)
        self.vote_data = 'source/input/votematrix-2010.dat'
        self.politicians = self.cache_models.Politicians()
        self.cache = self.cache_models.Votes()
        self.voting_key = {
            -9: "missing",
            1: "tellaye",
            2: "aye",
            3: "both",
            4: "no",
            5: "tellno"
        }

    def import_votes(self):
        data = self.csv_to_df(self.vote_data, delimiter='\t')
        mps = list(data.columns.values)
        for index, row in data.iterrows():
            vote = {
                "date": row["date"],
                "bill": row["Bill"],
                "vote_number": row["voteno"]
            }
            print "---\n", row["Bill"]
            print row["voteno"], row["date"]
            votes = []
            for col in mps[4:]:
                whip_id = col[4:]
                result = self.politicians.collection.find(
                    {"publicwhip_id": whip_id}
                ).limit(1)
                if result.count() > 0:
                    mp = {
                        "full_name": result[0]["full_name"],
                        "vote": self.voting_key[row[col]]
                    }
                    votes.append(mp)
            vote["votes"] = votes
            self.cache.write(vote)


class DebatesinParliament(CacheInterface):
    def __init__(self, verbose=True):
        CacheInterface.__init__(self)
        self.verbose = verbose
        self.text = self.speech_tools.TextHandler()
        self.cache = self.cache_models.Debates()
        self.mps = self.hansard.get_mps()

    def import_debates(self):
        print "\n\nImporting Parliament Debates\n"
        for mp in self.mps:
            mp_debates = self.hansard.get_mp_debates("commons", mp['person_id'])
            self._print_out(
                mp['name'],
                "Debate Count",
                mp_debates["info"]["total_results"]
            )
            if mp_debates:
                for result in mp_debates["rows"]:
                    sleep(1)
                    self._print_out("MP debate_id:", result["gid"], "")
                    output = self.hansard.get_debate(result["gid"])
                    if output:
                        self._get_debate(output)
                        print "-"

    def _get_debate(self, data):
        full_debate = {}
        start, sub, comment = data[0], data[1], data[2]
        full_debate["debate_id"] = start["debate_id"]
        if sub:
            sub_debate ={}
            sub_debate["debate_id"] = sub["debate_id"]
            han = self.hansard.get_full_debate(sub["debate_id"])
            topic, sub_topic, debate_content = han[0], han[1], han[2]
            self._print_out("MAIN TOPIC:", topic["debate_id"], topic["topic"])
            full_debate["topic"], full_debate["date"] = self._content(topic)
            sub_debate["topic"], sub_debate["date"] = self._content(sub_topic)
            self._print_out("SUB TOPIC:", sub["debate_id"], sub_debate["topic"])
            sub_debate["arguments"] = self._interate_debate(debate_content)
            self.cache.write(full_debate)
            self.cache.add_subdocument(full_debate["debate_id"], sub_debate)
        else:
            self._print_out("Primary TOPIC:", start["debate_id"], start["body"])
            if start["content_count"] > 0:
                full_debate["topic"], full_debate["date"] = self._content(start)
                han = self.hansard.get_full_debate(start["debate_id"], False)
                topic, sub_topic, debate_content = han[0], han[1], han[2]
                full_debate["arguments"] = self._interate_debate(debate_content)
            self.cache.write(full_debate)

    def _interate_debate(self, arguments):
        all_arguments = []
        previous_verse_id = ""
        argument = {}
        for entry in arguments:
            scrubbed_text = self.text.parse_raw_html(entry["body"])
            argument_id = entry["gid"]
            argument = {
                "argument_id": argument_id,
                "text": scrubbed_text
            }
            if "speaker" in entry and "person_id" in entry["speaker"]:
                firstname = entry["speaker"]["first_name"]
                lastname = entry["speaker"]["last_name"]
                person_id = entry["speaker"]["person_id"]
                name = "%s %s" % (firstname, lastname)
                speaker = {"name": name, "twfy_id": person_id}
                argument["speaker"] = speaker
                #print "\n\n%s Comment:\n" % name, scrubbed_text, "\n__\n"
            if not previous_verse_id == "":
                argument["previous_argument"] = previous_verse_id
            previous_verse_id = argument_id
            all_arguments.append(argument)
        return all_arguments

    def _content(self, topic):
        if "body" in topic:
            topic, date = topic["body"], topic["date"]
        else:
            topic, date = topic["topic"], topic["date"]
        return topic, date

    def _print_out(self, key, value, comment):
        print "  %-15s%-20s%-20s" % (key, value, comment)