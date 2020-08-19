"""
thanks to:
    https://stackoverflow.com/questions/44827930/evaluation-in-a-spacy-ner-model
"""

from __future__ import unicode_literals, print_function
import spacy
from spacy.util import minibatch, compounding

from spacy.gold import GoldParse
from spacy.scorer import Scorer

import os
import json
import sys

import pickle
import plac
import random


def evaluate(nerModel, examples):
    scorer = Scorer()
    for input_, annot in examples:
        docGoldText = nerModel.make_doc(input_)

        gold = GoldParse(docGoldText, entities = annot['entities'])
        predValue = nerModel(input_)
        scorer.score(predValue, gold)
    return scorer.scores


with open ('cucchiaio_ingredients_test_set.spacy', 'rb') as f:
	trainData = pickle.load(f)

nerModel = spacy.load('ingredients_NER_model')
results = evaluate(nerModel, trainData)

print(results)

"""
Here we have the output:

{'uas': 0.0, 'las': 0.0, 'las_per_type': {'': {'p': 0.0, 'r': 0.0, 'f': 0.0}}, 
'ents_p': 93.87494683113569, 'ents_r': 96.88323090430202, 'ents_f': 95.35536833009289, 
'ents_per_type': 
	{'AMT': {'p': 97.46376811594203, 'r': 98.53479853479854, 'f': 97.99635701275045}, 
	'ING': {'p': 90.69767441860465, 'r': 95.44303797468355, 'f': 93.00986842105263},
	'MT': {'p': 0.0, 'r': 0.0, 'f': 0.0}},
	'tags_acc': 0.0, 'token_acc': 100.0, 'textcat_score': 0.0, 'textcats_per_cat': {}}
"""

"""
howto read the result:
    https://stackoverflow.com/questions/50644777/understanding-spacys-scorer-output

19-jun-20

{'uas': 0.0, 'las': 0.0, 'las_per_type': {'': {'p': 0.0, 'r': 0.0, 'f': 0.0}}, 'ents_p': 96.37139807897546, 'ents_r': 96.37139807897546, 'ents_f': 96.37139807897546, 'ents_per_type': {'NAME': {'p': 97.20028715003589, 'r': 96.85264663805437, 'f': 97.02615549982086}, 'AMOUNT': {'p': 95.16765285996055, 'r': 99.38208032955716, 'f': 97.22921914357681}, 'O': {'p': 96.53465346534654, 'r': 88.23529411764706, 'f': 92.19858156028369}}, 'tags_acc': 0.0, 'token_acc': 100.0, 'textcat_score': 0.0, 'textcats_per_cat': {}}
[Finished in 3.2s]
"""