import re
import os.path
import csv
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.chunk import ChunkParserI, tree2conlltags
from nltk.chunk.util import conlltags2tree
from sklearn.linear_model import LogisticRegression
import pandas as pd
import os


class Relations():
    def __init__(self):
        pass

    def extract_triples(
            self, sentence, normalize=False, lex_syn_constraints=False,
            allow_unary=False, short_rel=False, export=False):
        print "---\n", sentence
        np_chunks_tree = self._get_chunks(sentence)
        # print np_chunks_tree
        reverb = Reverb(
            sentence, np_chunks_tree, normalize, lex_syn_constraints,
            allow_unary, short_rel, export
        )
        triples = reverb.extract_triples()
        return triples

    def _get_chunks(self, sentence):
        # print " [x] Requesting chunking for a sentence"
        chunker = BigramChunker()
        chunked_sent = chunker.parse(sentence)
        # print " [.] Got ", (chunked_sent,)
        # np_chunks_tree = nltk.Tree(chunked_sent)
        return chunked_sent


class Reverb():
    """
    Approximately Reverb (regex part of it) translation.
    """
    def __init__(self, sentence, np_chunks_tree, normalize,
                 lex_syn_constraints, allow_unary, short_rel, export=False):
        """
        :param lex_syn_constraints: Use syntactic and lexical constraints.
        :param allow_unary: allow unary relations ("the book is published").
        """
        self.sentence = sentence
        self.np_chunks_tree = np_chunks_tree
        self.normalize = normalize
        self.lex_syn_constraints = lex_syn_constraints
        self.allow_unary = allow_unary
        self.pos_tags = nltk.pos_tag(nltk.word_tokenize(self.sentence))
        self.short_rel = short_rel
        self.export = export
        self.extra_features = {}

    def extract_triples(self):
        """
        Extracts (subject predicate object) triples from the given sentence. Returns a list of triples.
        """
        # verb = optional adverb [modal or other verbs] optional particle/adverb
        # print "*rel: %s" % tree
        triples = self._get_triples()
        return triples

    def _get_triples(self):
        triples = []
        rel_indices, relations = self._get_relations()
        for idx, relation in enumerate(relations):
            left_arg = self._get_left_arg(relation, rel_indices[idx][0])
            right_arg = self._get_right_arg(relation, rel_indices[idx][1])
            if self.lex_syn_constraints:
                if not self._is_relation_lex_syn_valid(relation, rel_indices[idx]):
                    #print "[x]syntactic constraints not met"
                    continue
            if not self.allow_unary and right_arg == "":
                continue
            if left_arg == "":
                # todo: try to extract left_arg even the subject is for example before comma like in
                # the following sentence (for "has" relation):
                # "This chassis supports up to six fans , has a complete black interior"
                continue
            confidence_function = ConfidenceFunction(
                self.sentence,
                relation,
                left_arg,
                right_arg,
                rel_indices[idx],
                self.extra_features,
                True
            )
            if self.export:
                confidence_function.write_features()
            result = confidence_function.classify()
            print "***", result, left_arg, relation, right_arg
            #triples.append((left_arg, relation, right_arg))
        return triples

    def _get_relations(self):
        relations = []
        normalized_relations = []
        rel_indices = []
        index = 0
        verb = "<RB>?<MD|VB|VBD|VBP|VBZ|VBG|VBN><RP>?<RB>?"
        preposition = "<RB>?<IN|TO|RP><RB>?"
        word = "<PRP$|CD|DT|JJ|JJS|JJR|NN|NNS|NNP|NNPS|POS|PRP|RB|RBR|RBS|VBN|VBG>"
        regex_parser = None
        if self.short_rel:
            short_rel_pattern = r'(%s(%s)?)+' % (verb, preposition)
            grammar_short = "REL: {%s}" % short_rel_pattern
            regex_parser = nltk.RegexpParser(grammar_short)
        else:
            long_rel_pattern = r'(%s(%s*(%s)+)?)+' % (verb, word, preposition)
            grammar_long = "REL: {%s}" % long_rel_pattern
            regex_parser = nltk.RegexpParser(grammar_long)
        tree = regex_parser.parse(self.pos_tags)
        for t in tree:
            if type(t) == nltk.Tree and t.node == "REL":
                rel_ind = (index, index + len(t.leaves()))
                rel_indices.append(rel_ind)
                relation = " ".join(map(lambda x: x[0], t.leaves()))
                relation_pos = " ".join(map(lambda x: x[1], t.leaves()))
                relations.append(relation)
                if self.normalize:
                    norm_rel = self.verb_rel_normalize(rel_ind)
                else:
                    norm_rel = relation
                normalized_relations.append(norm_rel)
                index += len(t.leaves())
            else:
                index += 1
        return rel_indices, normalized_relations

    def _get_left_arg(self, relation, left_rel_border):
        self.extra_features["NP_left_of_x"] = False
        self.extra_features["PREP_left_of_x"] = False
        candidate = ""
        #count words to see if we are still on the left side of the relation
        word_ind = 0
        for t in self.np_chunks_tree:
            if type(t) != nltk.Tree:
                word_ind += 1
            else:
                # don't need to check if t.node == "NP" because NP chunker
                word_ind += len(t.leaves())
                # leaves = " ".join(map(lambda x: x.split("/")[0], t.leaves()))
                leaves = " ".join(map(lambda x: x[0], t.leaves()))
                # check if we are already on the right side of the relation
                if word_ind > left_rel_border:
                    break
                if len(t) == 1:
                    word = t[0][0]
                    tag = t[0][1]
                    if tag == "EX":
                        # first argument can't be an existential "there"
                        continue
                    if tag == "WDT" or tag == "WP$" or tag == "WRB" or tag == "WP":
                        #first argument can't be a Wh word
                        continue
                    if tag == "IN":
                        # first argument can't be a preposition
                        self.extra_features["PREP_left_of_x"] = True
                        continue
                    if word == "that" or word == "which":
                        continue
                    reflexive_pronouns = ["myself", "yourself", "himself",
                                          "herself", "itself", "oneself",
                                          "ourselves", "ourself", "yourselves",
                                          "themselves"]
                    if word in reflexive_pronouns:
                        continue
                cand = leaves
                # FIGURE THIS OUT
                # First argument can't match, this was enabled
                # "ARG1, REL" "ARG1 and REL" or "ARG1, and REL"
                clean_cand = self.clean_string(cand)
                clean_relation = self.clean_string(relation)
                if re.findall(
                        r"%s\s*,\s*%s" % (clean_cand, clean_relation),
                        self.sentence):
                    continue
                if re.findall(
                        r"%s\s*and\s*%s" % (clean_cand, clean_relation),
                        self.sentence):
                    continue
                if re.findall(
                        r"%s\s*,and\s*%s" % (clean_cand, clean_relation),
                        self.sentence):
                    continue
                arg_indices = (word_ind - len(t.leaves()), word_ind)
                if candidate != "":
                    self.extra_features["NP_left_of_x"] = True
                if self.normalize:
                    candidate = self.arg_normalize(arg_indices)
                else:
                    candidate = cand
                # First argument should be closest to relation that passes
                # through filters (means don't break the loop here)
        return candidate

    def _get_right_arg(self, relation, right_rel_border):
        self.extra_features["NP_right_of_y"] = False
        found = False
        candidate = ""
        word_ind = 0
        #count words to see if we are on the right side of the relation
        for t in self.np_chunks_tree:
            if type(t) != nltk.Tree:
                word_ind += 1
            else:
                word_ind += len(t.leaves())
                leaves = " ".join(map(lambda x: x[0], t.leaves()))
                if word_ind < right_rel_border:
                    # check if we are still on the left side of the relation
                    continue
                if len(t) == 1:
                    word = t[0][0]
                    tag = t[0][1]
                    if tag == "WDT" or tag == "WP$" or tag == "WRB" or tag == "WP":
                        #first argument can't be a Wh word
                        continue
                    if word == "which":
                        continue
                cand = leaves
                # FIGURE THIS OUT
                # Second argument should be adjacent to the relation
                clean_cand = self.clean_string(cand)
                clean_relation = self.clean_string(relation)
                clean_sentence = self.clean_string(self.sentence)
                if not re.findall(
                        r"%s\s*%s" % (clean_relation, clean_cand),
                        clean_sentence):
                    #print " [*]Second argument should be adjacent to the relation"
                    continue
                arg_indices = (word_ind - len(t.leaves()), word_ind)
                if not found:
                    if self.normalize:
                        candidate = self.arg_normalize(arg_indices)
                    else:
                        candidate = cand
                    # Second argument should be closest to relation that passes through filters (break the loop)
                    found = True
                else:
                    self.extra_features["NP_right_of_y"] = True
        return candidate

    def _is_relation_lex_syn_valid(self, relation, rel_indices):
        """
        Checks syntactic and lexical constraints on the relation.
        """
        pos_tags = map(lambda x: x[1], self.pos_tags[rel_indices[0]: rel_indices[1]])
        rel_words = map(lambda x: x[0], self.pos_tags[rel_indices[0]: rel_indices[1]])
        # these POS tags and words cannot appear in relation: CC, ",", PRP, "that", "if":
        forbidden_tags = ["CC", "PRP"]
        if len(set(pos_tags).intersection(set(forbidden_tags))) > 0:
            #print " [*]Forbidden pos tags"
            return False
        forbidden_words = [",", "that", "if"]
        if len(set(rel_words).intersection(set(forbidden_words))) > 0:
            # print "forbidden words"
            return False
        if len(rel_words ) < 2:
            # relation shouldn't be a single character
            #print " [*]relation shouldn't be a single character"
            return False
        # The POS tag of the first verb in the relation cannot be VBG or VBN:
        for tag in pos_tags:
            if tag[:2] == "VB":
                if tag == "VBG" or tag == "VBN":
                    #print " [*]First verb in the relation cannot be VBG or VBN"
                    return False
                else:
                    break
        # The previous tag can't be an existential "there" or a TO:
        if self.pos_tags[rel_indices[0] - 1][1] in ["EX", "TO"]:
            #print " [*]Previous tag can't be an existential 'there' or a TO"
            return False
        return True

    def verb_rel_normalize(self, rel_indices):
        ignore_pos_tags = []
        ignore_pos_tags.append("MD")  # can, must, should
        ignore_pos_tags.append("DT")  # the, an, these
        ignore_pos_tags.append("PDT")  # predeterminers
        ignore_pos_tags.append("WDT")  # wh-determiners
        ignore_pos_tags.append("JJ")  # adjectives
        ignore_pos_tags.append("RB")  # adverbs
        ignore_pos_tags.append("PRP$")  # my, your, our
        # remove leading "be", "have", "do"
        aux_verbs = []
        aux_verbs.append("be")
        aux_verbs.append("have")
        aux_verbs.append("do")
        no_noun = True
        relation = ""
        pos_tags = self.pos_tags[rel_indices[0]:rel_indices[1]]
        for _word, pos_tag in pos_tags:
            if pos_tag[0] == "N":
                no_noun = False
                break
        lmtzr = WordNetLemmatizer()
        for ind, (word, pos_tag) in enumerate(pos_tags):
            is_adj = pos_tag[0] == "J"
            # This is checking for a special case where the relation phrase
            # contains an adjective, but no noun. This covers cases like
            # "is high in" or "looks perfect for" where the adjective carries
            # most of the semantics of the relation phrase. In these cases, we
            # don't want to strip out the adjectives.
            keep_adj = is_adj and no_noun
            if pos_tag in ignore_pos_tags and not keep_adj:
                continue
            else:
                if pos_tag[0] in ["N", "V"]:
                    pos = pos_tag[0].lower()
                    # moved code below into if loop
                    pos = pos_tag[0].lower()
                    new_word = lmtzr.lemmatize(word, pos)
                    if new_word \
                            in aux_verbs \
                            and ind + 1 < len(pos_tags) \
                            and pos_tags[ind + 1][1][0] == "V":
                        pass
                    else:
                        relation += " " + new_word
        return relation.strip()

    def arg_normalize(self, arg_indices):
        """If the field contains a proper noun, don't normalize
            If the field contains a tag starting with N, return the rightmost one - stemmed
            Otherwise, don't normalize.
         """
        contains_proper_noun = False
        last_noun_index = -1
        start = arg_indices[0]
        end = arg_indices[1]
        pos_tags = self.pos_tags[start:end]
        for ind, (_word, pos_tag) in enumerate(pos_tags):
            if pos_tag in ["NNP", "NNPS"]:
                contains_proper_noun = True
            if pos_tag[0] == "N":
                last_noun_index = ind
        if contains_proper_noun or last_noun_index == -1:
            not_changed = map(lambda x: x[0], self.pos_tags[start:end])
            not_changed = " ".join(not_changed)
            return not_changed
        else:
            last_noun = pos_tags[last_noun_index][0]
            lmtzr = WordNetLemmatizer()
            new_word = lmtzr.lemmatize(last_noun, "n")
            return new_word

    def clean_string(self, dirty_string):
        clean = dirty_string
        clean = clean.replace("(", "\(", 5)
        clean = clean.replace(")", "\)", 5)
        clean = clean.replace("[", "\[", 5)
        clean = clean.replace("]", "\]", 5)
        return clean


class ConfidenceFunction():
    reg = 1000.
    classifier = LogisticRegression(C=reg)
    relation_file = "%s/utils/relations/relation_data.csv" % os.curdir
    relations = pd.read_csv(relation_file)
    features, response = relations.iloc[:, 1:16], relations.iloc[:, 0]
    classifier.fit(features, response)
    
    def __init__(self, sent, r, x, y, rel_index, extra_feats, export):
        self.output_file = 'features_output.csv'
        self.features = {}
        #self.features.update(extra_feats)
        self.features = extra_feats
        self.s = sent
        self.r = r
        self.r_index = rel_index
        self.left_arg = x
        self.right_arg = y
        self.export = export
        if self.export:
            self._create_file()
        self._get_features()

    def _create_file(self):
        if not os.path.isfile(self.output_file):
            with open(self.output_file, 'w') as f:
                w = csv.DictWriter(f, self.features.keys())
                w.writeheader()

    def _tokenize(self):
        self.s_tokens = nltk.word_tokenize(self.s)
        self.r_tokens = nltk.word_tokenize(self.r)
        self.left_tokens = nltk.word_tokenize(self.left_arg)
        self.right_tokens = nltk.word_tokenize(self.right_arg)
        s, r = len(self.s_tokens), len(self.r_tokens)
        x, y = len(self.left_arg), len(self.right_arg)
        self.features["xry_equals_s"] = s == x + r + y

    def _get_features(self):
        if self.export:
            self.features["sentence"] = unicode(self.s).encode("utf-8")
            self.features["relation"] = unicode(self.r).encode("utf-8")
            self.features["left_arg"] = unicode(self.left_arg).encode("utf-8")
            self.features["right_arg"] = unicode(self.right_arg).encode("utf-8")
        self._tokenize()
        self._relation_features()
        self._sentence_features()
        self._relation_features()
        self._lexical_features()
        self._semantic_features()
        #print self.features

    def _sentence_features(self):
        self.features["len(s)_ls_10"] = len(self.s_tokens) <= 10
        self.features["len(s)_gt_20"] = len(self.s_tokens) > 20
        self.features["len(s)_gt_10_less_20"] = \
            10 < len(self.s_tokens) < 20
        self.features["s_begins_with_x"] = \
            self.s_tokens[0] == self.left_tokens[0]

    def _relation_features(self):
        if len(self.r_tokens) > 1:
            last_word = self.r_tokens[len(self.r_tokens)-1]
            if last_word == ".":
                last_word = self.r_tokens[len(self.r_tokens)-2]
            self.features["last_r_prep_is_for"] = last_word == "for"
            self.features["last_r_prep_is_on"] = last_word == "on"
            self.features["last_r_prep_is_of"] = last_word == "of"
            self.features["last_r_prep_is_to"] = last_word == "to"
            self.features["last_r_prep_is_in"] = last_word == "in"

    def _lexical_features(self):
        self.features["WH_left_of_r"] = False
        self.features["CC_left_of_r"] = False
        s_pos = nltk.pos_tag(self.s_tokens)
        for w, pos in s_pos[:self.r_index[0]]:
            if w[:2].lower() == "wh":
                self.features["WH_left_of_r"] = True
            if pos == "CC":
                self.features["CC_left_of_r"] = True

    def _semantic_features(self):
        left_pos_tags = [pos for (_, pos) in nltk.pos_tag(self.left_tokens)]
        right_pos_tags = [pos for (_, pos) in nltk.pos_tag(self.right_tokens)]
        self.features["x_is_propernoun"] = "NNP" in left_pos_tags
        self.features["y_is_propernoun"] = "NNP" in right_pos_tags

    def _transform(self, dictionary):
        excluded = [
            "sentence",
            "sentence",
            "relation",
            "left_arg",
            "right_arg",
            "last_r_prep_is_on",
            "PREP_left_of_x"
        ]
        for x in excluded:
            if x in dictionary.keys():
                dictionary.pop(x)

        for key in dictionary:
            if dictionary[key]:
                dictionary[key] = int(1)
            elif not dictionary[key]:
                dictionary[key] = int(0)
        return dictionary

    def write_features(self):
        with open(self.output_file, 'a') as f:
            w = csv.DictWriter(f, self.features.keys())
            #w.writeheader()
            w.writerow(self.features)

    def classify(self):
        transformed = self._transform(self.features)
        data_frame = pd.Series(transformed)
        return ConfidenceFunction.classifier.predict(data_frame)


class BigramChunker(ChunkParserI):
    def __init__(self):
        train_sents = nltk.corpus.conll2000.chunked_sents('train.txt', chunk_types=['NP'])
        train_data = [[(t, c) for _, t, c in tree2conlltags(sent)] for sent in train_sents]
        unigram_tagger = nltk.UnigramTagger(train_data)
        self.tagger = nltk.BigramTagger(train_data, backoff=unigram_tagger)

    def parse(self, sentence):
        tokenized = nltk.pos_tag(nltk.word_tokenize(sentence))
        pos_tags = [pos for (_, pos) in tokenized]
        tagged_pos_tags = self.tagger.tag(pos_tags)
        chunktags = [chunktag for (pos, chunktag) in tagged_pos_tags]
        conlltags = [
            (word, pos, chunktag) for ((word, pos), chunktag) in zip(tokenized, chunktags)
        ]
        return conlltags2tree(conlltags)