import random


class Bayes:
    def __init__(self):
        self.training_features = []
        self.test_features = []
        self.errors = []

    def set_word_features(self, features):
        self.word_features = features

    def set_feature_extractor(self, feature_extractor):
        self.feature_extractor = feature_extractor

    def build_classifier(self, content_category_data):
        content_category_data = self.randomize_content(content_category_data)
        print '\nBuilding Bayes Classification Features'
        category_class_features = [
            (self.feature_extractor(content_category[0]), content_category[1])
            for content_category in content_category_data
        ]
        category_class_cutoff = len(category_class_features)*3/4

        self.training_features = category_class_features[:category_class_cutoff]
        self.test_features = category_class_features[category_class_cutoff:]
        print 'train on %d instances, test on %d instances' % (
            len(self.training_features), len(self.test_features)
        )

        self.classifier = NaiveBayesClassifier.train(self.training_features)

    def test_classifier(self):
        self.classifier.show_most_informative_features(15)
        print 'accuracy:', \
            nltk.classify.accuracy(self.classifier, self.test_features),\
            '\n'

    def classify(self, content):
        self.classification = self.classifier.classify(
            self.feature_extractor(content)
        )
        return self.classification

    def randomize_content(self, content_list):
        new_list = []
        while content_list:
            element = random.choice(content_list)
            new_list.append(element)
            content_list.remove(element)
        return new_list