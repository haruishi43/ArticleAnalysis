# -*- coding: utf-8 -*-

import math

from janome.tokenizer import Tokenizer


class NaiveBayes:

    def __init__(self):
        self.vocabs = set()  # vocabulary set
        self.word_counter = {}  # {category : { words : n, ... }}
        self.category_counter = {}  # {category : n}
        self.prior_prob = {}  # {category : P(category)}
        self.confusion = {}  # {category : {category : n}}
        self.norm_confusion = {}  # {category : {category : float}}

    def word_countup(self, word, category):
        """ incrementor for words in categories """
        self.word_counter.setdefault(category, {})
        self.word_counter[category].setdefault(word, 0)
        self.word_counter[category][word] += 1
        self.vocabs.add(word)

    def category_countup(self, category):
        """ incrementor for categories """
        self.category_counter.setdefault(category, 0)
        self.category_counter[category] += 1
        # update prior_prob as well
        self.prior_prob[category] = float(self.category_counter[category]) / sum(self.category_counter.values())

    def confusion_coutup(self, real, assumption):
        """ incrementor for confusion matrix """
        self.confusion.setdefault(real, {})
        self.confusion[real].setdefault(assumption, 0)
        self.confusion[real][assumption] += 1
    
    def normalize_confusion(self):
        """ normalize confusion matrix """
        categories = sorted(self.category_counter.keys())
        
        # initailize normalized confusion matrix
        for real_cat in categories:
            self.norm_confusion.setdefault(real_cat, {})
            for assump_cat in categories:
                self.norm_confusion[real_cat].setdefault(assump_cat, 0)
        
        # calculate ratio and change the value
        for real_cat, assumptions in self.confusion.items():
            tot = sum(assumptions.values())
            for assump_cat, value in assumptions.items():
                self.norm_confusion[real_cat][assump_cat] = value / tot

    def train(self, doc, category):
        """ train classifier based on input text and category """
        words = self.get_words_revised(doc)
        for word in words:
            self.word_countup(word, category)
        self.category_countup(category)

    def test(self, doc, category):
        """ test the cassifier and append confusion matrix """
        assump = self.classifier(doc)
        self.confusion_coutup(category, assump)
        # FIXME: create an accuracy counter here
        return assump

    def classifier(self, doc):
        """ classify a text and returns the category number """
        best_category = None
        max = -float("inf")  # initialize to the lowest value
        word = self.get_words_revised(doc)
        
        for category in self.category_counter.keys():
            prob = self.score(word, category)
            if prob > max:
                max = prob
                best_category = category
        return best_category

    def score(self, words, category):
        """ tally up the score based on words """
        # use log to prevent underflow
        score = math.log(self.prior_prob[category])
        for word in words:
            score += math.log(self.word_prob(word, category))
        return score

    def in_category(self, word, category):
        """ return how many times a word appeared in a category """
        if word in self.word_counter[category]:
            return float(self.word_counter[category][word])
        return 0.0

    def word_prob(self, word, category):
        """
        calculate conditional probability P(word|category)
        also added smoothing
        """
        prob = (
            self.in_category(word, category) + 1.0) / \
            (sum(self.word_counter[category].values()) +
             len(self.vocabs) * 1.0)
        return prob

    def get_words(self, doc):
        """ creates a tuple of words from a text """
        words = []
        tokens = Tokenizer().tokenize(doc)
        for token in tokens:
            words.append(token.surface)
        words = [word.lower() for word in words]
        return tuple(w for w in words)
    
    def get_words_revised(self, doc):
        """ creates a tuple of words from a text """
        words = []
        tokens = Tokenizer().tokenize(doc)
        for token in tokens:
            pos = token.part_of_speech.split(',')
            if pos[1] in ['数']:
                continue
            if pos[0] in ['名詞', '動詞', '形容詞']:
                words.append(token.base_form)
        words = [word.lower() for word in words]
        return words

    def get_confusion_matrix(self):
        """ function that returns the confusion matrix """
        self.normalize_confusion()
        return self.norm_confusion
