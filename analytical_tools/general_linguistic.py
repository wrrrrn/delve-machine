from nltk.corpus import stopwords, wordnet
from nltk.collocations import BigramCollocationFinder, TrigramCollocationFinder
from nltk.metrics import BigramAssocMeasures, TrigramAssocMeasures
from nltk.stem.wordnet import WordNetLemmatizer
from gensim import corpora, models as gensim_models
from goose import Goose
from textblob import TextBlob
import nltk
import re
import os

goose = Goose()


class TextHandler:
    def __init__(self):
        self.text = ""
        self.parsed_text = ""
        self.lemmatizer = WordNetLemmatizer()
        self.stopwords = stopwords.words('english')
        self.bigram_score_function = BigramAssocMeasures.chi_sq
        self.trigram_score_function = TrigramAssocMeasures.chi_sq
        self.top_ngram_count = 400
        self.text_blob = TextBlob

    def get_words(self, text, with_punctuation=True, remove_stopwords=False):
        self.text = text
        if with_punctuation:
            tokens = nltk.word_tokenize(self.text)
        else:
            words = nltk.word_tokenize(self.text)
            tokens = [
                w.lower().rstrip('.') for w in words
                if re.match("([A-Z]|[a-z]|\s|\(|\)|-|[0-9]|\')", w)
            ]

        if remove_stopwords:
            tokens = [
                w.lower().rstrip('.') for w in tokens
                if w not in self.stopwords
            ]
        return tokens

    def get_definitions(self, word):
        return wordnet.synsets(word)

    def lemma(self, word):
        return self.lemmatizer.lemmatize(word)

    def get_sentences(self, text):
        self.text = text
        return nltk.sent_tokenize(self.text)

    def get_bigrams(self, words):
        bigram_finder = BigramCollocationFinder.from_words(words)
        self.biagrams = bigram_finder.nbest(
            self.bigram_score_function,
            self.top_ngram_count
        )
        return self.biagrams

    def get_trigrams(self, words):
        trigram_finder = TrigramCollocationFinder.from_words(words)
        self.trigrams = trigram_finder.nbest(
            self.trigram_score_function,
            self.top_ngram_count
        )
        return self.trigrams

    def unique_lemmas(self, tokens):
        lemmas = [self.lemma(x) for x in tokens]
        return set(lemmas)

    def unique(self, seq):
        seen = set()
        seen_add = seen.add
        return [x for x in seq if x not in seen and not seen_add(x)]

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

    def parse_raw_html(self, raw):
        try:
            self.parsed_text = nltk.clean_html(raw)
            return self.parsed_text
        except Exception, e:
            print '->Unable to parse raw html. Error: %s' % e
            return False

    def get_semantic_details(self, word):
        word_dict = {}
        synset_detail = []
        wordnet_synset = ['word', 'wordnet_entry', 'part_of_speech', 'definition']
        synsets = self.get_definitions(word)
        for synset in synsets:
            word_detail = [
                word,
                synset.name,
                synset.lexname,
                synset.definition
            ]
            if word_detail:
                word_dict = dict(zip(wordnet_synset, word_detail))
                synonyms = self.get_synonyms(word, synset.name, synset.lemma_names)
                if synonyms:
                    word_dict['synonyms'] = synonyms
                synset_detail.append(word_dict)
        return synset_detail

    def get_synonyms(self, word, definition_word, synonyms):
        relevant_synonyms = []
        for synonym in synonyms:
            if synonym.lower() != word.lower() and synonym.lower() != definition_word.lower():
                relevant_synonyms.append(synonym)
        return relevant_synonyms


class TfidfModel(object):

    system_path = os.curdir
    corpus_path = '/analytical_tools/vectors/'
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