from analytical_tools import general_linguistic as lang
from gensim import corpora


class VectorCorpus(object):

    system_path = '/home/warren/System2/Dropbox/_code/virtualenvs'
    corpus_path = '/engine-datastore/analytical_tools/'
    corpus_data = system_path + corpus_path + 'vector_corpus.mm'
    vector_dict = system_path + corpus_path + 'vector_corpus.dict'

    def __init__(self):
        self.text_parser = lang.TextHandler()
        self.corpus = []
        self.documents = []
        self.vector_dictionary = []
        self.vector_dictionary_file = VectorCorpus.vector_dict

    def __iter__(self):
        for doc in self.corpus:
            # assume there's one document per line, tokens separated by whitespace
            yield self.corpora_dictionary.doc2bow(doc)

    def build(self, content):
        self.documents = [c for c in content if isinstance(c, basestring)]
        for doc in self.documents:
            document_words = self.text_parser.get_words(
                doc,
                remove_stopwords=True,
                with_punctuation=False
            )
            all_tokens = sum([document_words], [])
            tokens_once = set(
                word for word in set(all_tokens) if all_tokens.count(word) == 1
            )
            final_tokens = [
                word for word in document_words if word not in tokens_once
            ]
            self.vector_dictionary.append(final_tokens)
        self.corpora_dictionary = corpora.Dictionary(self.vector_dictionary)
        self.corpora_dictionary.save(self.vector_dictionary_file)
        self._create_corpus(self.documents)

    def _create_corpus(self, content):
        for doc in content:
            document_words = self.text_parser.get_words(
                doc,
                remove_stopwords=True,
                with_punctuation=False
            )
            self.corpus.append(document_words)
        corpus = [
            self.corpora_dictionary.doc2bow(doc)
            for doc in self.corpus
        ]
        self._save_corpus(VectorCorpus.corpus_data, corpus)

    def _save_corpus(self, path, corpus):
        corpora.MmCorpus.serialize(path, corpus)

