# -*- coding: utf-8 -*-

from janome.tokenizer import Tokenizer
from gensim import corpora, matutils

from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, confusion_matrix


class SVM:

    def __init__(self):
        self.dictionary = corpora.Dictionary()
        self.text_data = []
        self.label = []

    def create_dictionary(self, train_data):
        """ create dictionary and save it as text file """
        documents = []
        for data in train_data:
            words = self.get_words(''.join([data[1], data[2]]))
            documents.append(words)
        self.dictionary = corpora.Dictionary(documents)
        self.dictionary.filter_extremes(no_below=20, no_above=0.3)  # filter out extremes
        self.dictionary.save_as_text('common/dictionary.txt')

    def clean_data(self, doc, category):
        """ train classifier based on input text and category """
        self.dictionary = corpora.Dictionary.load_from_text('common/dictionary.txt')
        if bool(self.dictionary):
            words = self.get_words(doc)
            vec = self.dictionary.doc2bow(words)
            dense = list(matutils.corpus2dense([vec], num_terms=len(self.dictionary)).T[0])
            self.text_data.append(dense)
            self.label.append(category)

    def test(self):
        """ test the data against SVM """
        X_train, X_test, y_train, y_test = train_test_split(self.text_data, self.label, test_size=0.3)

        param_grid = [
            {'C': [1, 10, 100, 1000], 'kernel': ['linear']},
            {'C': [1, 10, 100, 1000], 'gamma': [0.001, 0.0001], 'kernel': ['rbf']},
        ]

        clf = GridSearchCV(SVC(), param_grid, cv=10)
        clf.fit(X_train, y_train)

        best_clf = clf.best_estimator_

        accuracy = best_clf.score(X_test, y_test)

        print("accuracy: {}".format(accuracy))

        y_true, y_pred = y_test, best_clf.predict(X_test)
        print(classification_report(y_true, y_pred))
        print(confusion_matrix(y_true, y_pred))

        self.clear()

    def clear(self):
        """ clear dictionary data """
        self.test_data = []
        self.label = []

    def get_words(self, doc):
        """ creates a array of words from a text """
        words = []
        tokens = Tokenizer().tokenize(doc)
        for token in tokens:
            words.append(token.surface)
        return [word.lower() for word in words]
