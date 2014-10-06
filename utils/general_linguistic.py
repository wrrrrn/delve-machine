from nltk.corpus import stopwords, wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora, models as gensim_models
from collections import Counter
from math import fabs
from fuzzywuzzy import process
from textblob import TextBlob
from textblob import Blobber
#from textblob_aptagger import PerceptronTagger
from goose import Goose
import nltk
import re
import os

goose = Goose()


def intersection(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    return list(set1.intersection(set2))


def unique_list(original_list):
    all_list_items = sum([original_list], [])
    unique_list = set(
        item for item in set(all_list_items) if all_list_items.count(item) == 1
    )
    return list(unique_list)


def multiple_occurence(original_list):
    all_list_items = sum([original_list], [])
    multiple_list = set(
        item for item in set(original_list) if all_list_items.count(item) > 1
    )
    return multiple_list


class TextHandler:
    def __init__(self):
        self.text = ""
        self.parsed_text = ""
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = stopwords.words('english')
        self.fuzzy_match = process
        self.text_blob = TextBlob
        #self.blob_parser = Blobber(pos_tagger=PerceptronTagger())

    def get_words(self, text, with_punctuation=True, remove_stopwords=False):
        self.text = text
        if with_punctuation:
            tokens = nltk.word_tokenize(self.text)
        else:
            words = nltk.word_tokenize(self.text)
            tokens = [
                w.lower().rstrip('.') for w in words
                if re.match("([A-Z]|[a-z]|\s|-|[0-9])", w)
            ]

        if remove_stopwords:
            tokens = [
                w.lower().rstrip('.') for w in tokens
                if w not in self.stopwords
            ]
        return tokens

    def get_sentences(self, text):
        self.text = text
        return nltk.sent_tokenize(self.text)

    def get_definitions(self, word):
        return wordnet.synsets(word)

    def lemma(self, word):
        return self.lemmatizer.lemmatize(word)

    def unique_lemmas(self, tokens):
        lemmas = [self.lemma(x) for x in tokens]
        return set(lemmas)

    def unique(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x not in seen and not seen_add(x)]

    def parts_of_speech(self, text, tagger="nltk"):
        if tagger == "nltk":
            return nltk.pos_tag(text)
        #elif tagger == "textblob":
        #    b2 = self.blob_parser(text)
        #    return b2.tags

    def get_named_entities(self, words):
        named_entities = []
        chunked_entities = nltk.ne_chunk(nltk.pos_tag(words), binary=False)
        named_chunks = [c for c in chunked_entities if hasattr(c, 'node')]
        for chunk in named_chunks:
            named_entities.append(
                (' '.join(c[0] for c in chunk.leaves()), chunk.node,)
            )
        return named_entities

    def get_all_entities(self, text):
        all_named_entities = []
        sentences = self.get_sentences(text)
        for sentence in sentences:
            words = self.get_words(sentence)
            entities = self.get_named_entities(words)
            if entities:
                all_named_entities.extend([entity for entity, tag in entities])
        return all_named_entities

    def parse_html(self, html):
        try:
            article = goose.extract(raw_html=html)
            text = article.cleaned_text
            return text
        except IOError, e:
            print '->Unable to parse raw html. Error: %s' % e
            return False
        except UnicodeDecodeError, e:
            print '->Unable to parse unicode. Error: %s' % e
            new_html = html.decode('utf-8', errors='replace')
            article = goose.extract(raw_html=new_html)
            text = article.cleaned_text
            return text

    def parse_raw_html(self, raw):
        try:
            self.parsed_text = nltk.clean_html(raw)
            return self.parsed_text
        except Exception, e:
            print '->Unable to parse raw html. Error: %s' % e
            return False


class TfidfModel(object):

    system_path = os.curdir
    corpus_path = '/utils/vectors/'
    corpus_data = system_path + corpus_path + 'vector_corpus.mm'
    vector_dict = system_path + corpus_path + 'vector_corpus.dict'

    def __init__(self):
        self.text_parser = TextHandler()
        self.dictionary_map = {}
        self.corpus_data = TfidfModel.corpus_data
        self.vector_dict = TfidfModel.vector_dict

    def load(self, corpus_file=False, dictionary_file=False):
        if corpus_file and dictionary_file:
            self.vector_corpus = self._load_corpus(corpus_file)
            self.vector_dictionary = self._load_dictionary(dictionary_file)
        else:
            self.vector_corpus = self._load_corpus(self.corpus_data)
            self.vector_dictionary = self._load_dictionary(self.vector_dict)

        self.dictionary_map = self._dictionary_mapping(self.vector_dictionary)
        self.model = gensim_models.TfidfModel(self.vector_corpus)
        return self.model

    def classify(self, words, score=False):
        doc = self._transform(words)
        tf = sorted(
            [(self.dictionary_map[word_score[0]], word_score[1]) for word_score in doc],
            key=lambda word: word[1])
        if score:
            return tf
        else:
            tf_id2word = []
            for word_score in tf:
                try:
                    mapped_word = self.dictionary_map[word_score[0]]
                    tf_id2word.append(mapped_word)
                except Exception, e:
                    tf_id2word.append(word_score[0])
            top_tf_words = tf_id2word[-20:]
            return sorted(top_tf_words, reverse=True)

    def _dictionary_mapping(self, dictionary):
        dictionary_map = {}
        token2id = dictionary.token2id
        for word, word_id in token2id.items():
            dictionary_map[word_id] = word
        return dictionary_map

    def _transform(self, words):
        #words = self.text_parser.get_words(words,remove_stopwords=True,with_punctionation=False)
        return self.model[self.vector_dictionary.doc2bow(words)]

    def _load_corpus(self, path):
        return corpora.MmCorpus(path)

    def _load_dictionary(self, path):
        return corpora.Dictionary.load(path)


class Summerizer:
    def __init__(self):
        self.ideal = 20.0
        self.stopwords = stopwords.words('english')
        self.text_handler = TextHandler()

    def summarize(self, title, text):
        summaries = []
        sentences = self.text_handler.get_sentences(text)
        keys = self._keywords(text)
        title_words = self.text_handler.get_words(
            title,
            with_punctuation=False
        )
        if len(sentences) <= 5:
            return sentences
        #score sentences, and use the top 5 sentences
        ranks = self._score(sentences, title_words, keys).most_common(5)
        for rank in ranks:
            summaries.append(rank[0])
        return summaries[:3]

    def _score(self, sentences, title_words, keywords):
        length = len(sentences)
        ranks = Counter()
        for i, s in enumerate(sentences):
            sentence = self.text_handler.get_words(s, with_punctuation=False)
            title_feature = self._title_score(title_words, sentence)
            sentence_length = self._length_score(sentence)
            position = self._sentence_position(i+1, length)
            sbs_feature = self._sbs(sentence, keywords)
            dbs_feature = self._dbs(sentence, keywords)
            frequency = (sbs_feature + dbs_feature) / 2.0 * 10.0
            #weighted average of scores from four categories
            total_score = (
                title_feature*1.5 + frequency*2.0 +
                sentence_length*1.0 + position*1.0
            ) / 4.0
            ranks[s] = total_score
        return ranks

    def _sbs(self, words, keywords):
        score = 0.0
        if len(words) == 0:
            return 0
        for word in words:
            if word in keywords:
                score += keywords[word]
        return (1.0 / fabs(len(words)) * score)/10.0

    def _dbs(self, words, keywords):
        if len(words) == 0:
            return 0
        summ = 0
        first = []
        second = []
        for i, word in enumerate(words):
            if word in keywords:
                score = keywords[word]
                if first == []:
                    first = [i, score]
                else:
                    second = first
                    first = [i, score]
                    dif = first[0] - second[0]
                    summ += (first[1]*second[1]) / (dif ** 2)
        # number of intersections
        k = len(set(keywords.keys()).intersection(set(words))) + 1
        return 1/(k*(k+1.0))*summ

    def _keywords(self, text):
        """
            get the top 10 keywords and their frequency scores
            ignores blacklisted words in stopWords,
            counts the number of occurrences of each word
        """
        text = self.text_handler.get_words(text, with_punctuation=False)
        word_count = len(text)  # of words before removing blacklist words
        freq = Counter(x for x in text if x not in self.stopwords)
        min_size = min(10, len(freq))  # get first 10
        keywords = {x: y for x, y in freq.most_common(min_size)}  # recreate a dict
        for k in keywords:
            article_score = keywords[k]*1.0 / word_count
            keywords[k] = article_score * 1.5 + 1
        return keywords

    def _length_score(self, sentence):
        return 1 - fabs(self.ideal - len(sentence)) / self.ideal

    def _title_score(self, title, sentence):
        title = [x for x in title if x not in self.stopwords]
        count = 0.0
        for word in sentence:
            if word not in self.stopwords and word in title:
                count += 1.0
        return count/len(title)

    def _sentence_position(self, i, size):
        """
            different sentence positions indicate different
            probability of being an important sentence
        """
        normalized = i*1.0 / size
        if 0 < normalized <= 0.1:
            return 0.17
        elif 0.1 < normalized <= 0.2:
            return 0.23
        elif 0.2 < normalized <= 0.3:
            return 0.14
        elif 0.3 < normalized <= 0.4:
            return 0.08
        elif 0.4 < normalized <= 0.5:
            return 0.05
        elif 0.5 < normalized <= 0.6:
            return 0.04
        elif 0.6 < normalized <= 0.7:
            return 0.06
        elif 0.7 < normalized <= 0.8:
            return 0.04
        elif 0.8 < normalized <= 0.9:
            return 0.04
        elif 0.9 < normalized <= 1.0:
            return 0.15
        else:
            return 0