# -*- coding: utf-8 -*-

import random
from tqdm import tqdm
from pathlib import Path
import pickle

from common import scraper
from common.naivebayes import NaiveBayes
from common.svm import SVM

pickle_file = 'common/model.p'
svm_model_file = 'common/svm.p'


def create_dataset_nb(categories, k=10):
    """
    retrieve data from the database and create dataset
    cross-validation is considered with k-folds (default: 10)
    """
    all_data = []
    for i, _ in categories.items():
        # retrieve data for each category
        row_data = scraper.get_category_data(i)
        all_data += row_data

    # shuffle the data
    random.shuffle(all_data)

    # divide the data in to 'k' folds
    count = len(all_data)
    return [all_data[i * count // k: (i + 1) * count // k] for i in range(k)]


def train_nb(train_set):
    """
    train using obtained training set
    save trained naive bayes to pickle file
    """
    nb = NaiveBayes()

    print("training model from data...")
    for t in tqdm(train_set):
        nb.train(''.join([t[1], t[2]]), t[0])

    return nb


def test_nb(nb, test_set):
    """
    test classifier using obtained test set
    """
    correct = 0
    print("testing the model...")

    for t in tqdm(test_set):
        word = ''.join([t[1], t[2]])
        assump = nb.test(word, t[0])
        if str(assump) == str(t[0]):
            correct += 1

    accuracy = correct / len(test_set)
    print("Accuracy: {}".format(accuracy))

    return accuracy


def output_to_site_nb(link):
    """
    output the category name based on input url
    for rendering in the site
    """
    categories = scraper.categories_en
    nb = NaiveBayes()

    if Path(pickle_file).is_file():
        with open(pickle_file, 'rb') as f:
            nb = pickle.load(f)
    else:
        # train classifier if there is no pickle file
        # this could take a few minutes...
        nb = cross_validate_nb()

    # get title and doc of the url
    title, doc = scraper.get_testing_data(link)

    if title and doc:
        # classify
        cat_num = int(nb.classifier(''.join([title, doc])))
        cat_name = categories[cat_num]  # japanese class name
        # cat_name = scraper.categories_en[cat_num]  # english class name
        return cat_name
    else:
        return None


def cross_validate_nb():
    """
    cross validation function for NaiveBayes
    """
    categories = scraper.categories
    dataset = create_dataset_nb(categories)

    if not dataset:
        print("""
              You don't have any data stored in the database!
              Please download using:
              $ python manage.py get_data
              """)
        return None

    best_accuracy = 0.0
    accuracies = []
    nb = NaiveBayes()

    total_iteration = len(dataset)

    print("Total Iterations: {}".format(total_iteration))

    for i in range(total_iteration):
        print("Iteration: {}".format(i + 1))
        test_set = dataset[i]
        remainder = dataset[:i] + dataset[i + 1:]
        train_set = [item for sublist in remainder for item in sublist]
        tmp_nb = train_nb(train_set)
        accuracy = test_nb(tmp_nb, test_set)
        accuracies.append(accuracy)
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            # use the best accuracy for use in production
            nb = tmp_nb

    pickle.dump(nb, open(pickle_file, 'wb'))
    print("Saved to model.p")

    mean = sum(accuracies) / len(accuracies)
    std = (sum((x - mean) ** 2 for x in accuracies) / len(accuracies)) ** 0.5

    print("Mean accuracy: {}".format(mean))
    print("Standard deviation: {}".format(std))

    return nb


def print_confusion_matrix():
    """ Print out the confusion matrix for the trained model """
    nb = NaiveBayes()

    if Path(pickle_file).is_file():
        with open(pickle_file, 'rb') as f:
            nb = pickle.load(f)
    else:
        # train classifier if there is no pickle file
        # this could take a few minutes...
        nb = cross_validate_nb()

    mat = nb.get_confusion_matrix()

    print("\t1\t2\t3\t4\t5\t6\t7\t8")
    for cat, m in mat.items():
        print("{i0}\t{i1:.4f}\t{i2:.4f}\t{i3:.4f}\t{i4:.4f}\t{i5:.4f}\t{i6:.4f}\t{i7:.4f}\t{i8:.4f}"
              .format(i0=cat,
                      i1=m[1],
                      i2=m[2],
                      i3=m[3],
                      i4=m[4],
                      i5=m[5],
                      i6=m[6],
                      i7=m[7],
                      i8=m[8]))


def test_output_svm():
    """ Test output for svm """
    categories = scraper.categories
    dataset = create_dataset_nb(categories)

    if not dataset:
        print("""
              You don't have any data stored in the database!
              Please download using:
              $ python manage.py get_data
              """)
        return None

    svm = SVM()

    test_set = dataset[0]
    remainder = dataset[1:]
    train_set = [item for sublist in remainder for item in sublist]

    svm.create_dictionary(train_set)

    # clean data
    for t in train_set:
        svm.clean_data(' '.join([t[1], t[2]]), t[0])

    for t in test_set:
        svm.clean_data(' '.join([t[1], t[2]]), t[0])

    svm.test()
