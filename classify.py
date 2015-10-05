# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import (TfidfVectorizer, CountVectorizer,
                                             HashingVectorizer)

from sklearn.cross_validation import ShuffleSplit
from sklearn.svm import LinearSVC, SVC
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsOneClassifier, OneVsRestClassifier
from sklearn import cross_validation
from sklearn.metrics import confusion_matrix
from sklearn import preprocessing
from sklearn.externals import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression

from mlxtend.classifier import EnsembleClassifier

import sys
import pandas as pd
import numpy as np
import re
import os

if len(sys.argv) < 2:
    print "usage: {} [FILE.json]".format(sys.argv[0])
    sys.exit(0)

f = sys.argv[1]
csv = pd.read_json(f)

topics = list(set(csv['topic'].tolist()))

vectorizers = [
    CountVectorizer(ngram_range=(1, 2),
                    stop_words='english'),
   #CountVectorizer(ngram_range=(1, 3),
   #                stop_words='english'),
   #CountVectorizer(ngram_range=(1, 4),
   #                stop_words='english'),
]

classifiers = [
    #LinearSVC(loss='squared_hinge', penalty='l2', dual=False, tol=1e-4),
    #LogisticRegression(penalty='l2', solver='liblinear', dual=False, tol=1e-4)
    SVC(C=1.5, tol=1e-4, probability=True)
]

pipelines = []


splitter = ShuffleSplit(csv.shape[0], n_iter=10, test_size=0.2)
for v in vectorizers:
    print "> Running tests with {}".format(v)
    for classifier in classifiers:
        # print "  > Using classifier {}".format(classifier)
        accuracies = []
        f1s = []

        for train, test in splitter:
            pipeline = Pipeline([('vect', v),
                                 ('tfidf', TfidfTransformer(sublinear_tf=True,
                                                            use_idf=True)),
                                 ('clf', OneVsRestClassifier(classifier))])

            pipeline.fit(np.asarray(csv['title'][train]),
                         np.asarray(csv['topic'][train]))

            #print v.get_feature_names()
            y_test = csv['topic'][test]
            X_test = csv['title'][test]

            accuracies.append(pipeline.score(X_test, y_test))
            y_pred = pipeline.predict(X_test)

            for x, y, z in zip(X_test, y_test, y_pred):
                if y != z:
                    print "\n\n"
                    print re.sub(r'\s+', ' ', x), '\t', y, '\t', z
                    probas = zip(pipeline.predict_proba([x])[0],
                                 pipeline.classes_)
                    print sorted(probas, key=lambda x: -x[0])[:3]
                    print "\n\n"

            print confusion_matrix(y_pred, y_test)
            y_pred = y_pred.tolist()
            y_pred += y_test.tolist()
            y_pred = set(y_pred)
            print sorted(y_pred)

        accuracies = np.array(accuracies)
        f1s = np.array(f1s)
        print '    > Accuracy: {} ({})'.format(accuracies.mean(),
                                               accuracies.std()*2)
        pipeline = Pipeline([('vect', v),
                            #('tfidf', TfidfTransformer(sublinear_tf=True,
                            #                           use_idf=False)),
                             ('clf', OneVsOneClassifier(classifier))])
        pipelines.append(pipeline)
