[![Build Status](https://travis-ci.com/Toraudonn/ArticleAnalysis.svg?branch=master)](https://travis-ci.com/Toraudonn/ArticleAnalysis)

# Article Analysis

Want to know what kind of article you're about to read?

## ✨Article Classifier✨

Classify articles based on Naive Bayes Classifier😆
Trying to add CNN or RNN based classifier (if I can get more data)

* [Installation](#installation)
* [Quick Start](#quick-start)
* [Usage](#usage)
* [Classifier Accuracy](#classifier)
* [Thoughts](#thoughts)

<a name="installation"></a>
## Installation

### Prerequisites

- Python version 3.6

### Install Package

Create a new virtual environment if needed:

```bash
$ pip install virtualenv
$ cd /path/to/project/root
$ mkdir DjangoEnv
$ virtualenv DjangoEnv
$ source Django/bin/activate
```

Install packages:

```bash
$ pip install -r requirements.text
```

<a name="quick-start"></a>
## Quick Start

All of the models and databases are already built from the beginning and you can just use the one that comes in this github.
However, there are [custom commands](#usage) that you can use to get data and train the classifier.

To build and run the website:

```bash
$ cd articleclassifier
$ python manage.py runserver
```

Then access [`http://127.0.0.1:8000/`](http://127.0.0.1:8000/) in your browser.

<a name="usage"></a>
## Usage

### Commands:

- Get training data:

```bash
$ python manage.py get_data
```

- Train the model:

Used to train the classifier.

```bash
$ python manage.py train_model
```

- Print out confusion matrix:

```bash
$ python manage.py print_confusion_matrix
```

**This command also outputs accuracy in the cli.**

- Delete the database and model file (useful when you want to remove every data related files):

```bash
$ python manage.py delete_data
```
