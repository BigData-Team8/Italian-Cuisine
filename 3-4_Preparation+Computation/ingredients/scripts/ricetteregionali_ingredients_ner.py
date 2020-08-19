import os
import json
import sys
from lxml import html
from bs4 import BeautifulSoup
from bson import json_util

import spacy
nlp = spacy.load('ingredients_NER_model')

import redis

# use 'SELECT 2' in order to select the current DB
r = redis.Redis(db = 6, port = 6310)
# r = redis.StrictRedis('localhost', 6310, charset = 'utf-8', decode_responses = True)

def main():

	i = 0

	with open('ricetteregionali_ingredients_ORIG_unique_sort') as fp: 
		lines = fp.readlines() 
		for line in lines: 
			line = line.strip('\n').strip()
			ingredientPre = r.get('ricetteregionali:orig-to-pre:' + line).decode('utf-8')
			i += 1

			NER_result = NER_ingredient(ingredientPre)
			ingredient = NER_result[0]
			amount = NER_result[1]

			print(ingredientPre)
			print(ingredient.strip() + '\n')

			if (ingredient.strip() != ''):
				# 5. add the key-value pair into Redis
				# https://stackoverflow.com/questions/21768017/how-to-reverse-lookup-in-redis
				# r.set('ricetteregionali:pre-to-ner-ingredient:' + ingredientPre, ingredient.strip())
				# we invert, also, the key-pair value for reverse lookup
				r.set('ricetteregionali:pre-to-ner-amount:' + ingredientPre, amount.strip())

# NLP-NER extraction
def NER_ingredient(ingredient):
	doc = nlp(ingredient)

	ingredient = ''
	amount = ''

	for ent in doc.ents:
		if ent.label_ == 'ING': ingredient += ent.text + ' '
		if ent.label_ == 'AMT': amount += ent.text + ' '

	return [ ingredient, amount ]

# let's start ;-)
if __name__ == '__main__':
    main()
    # print('\nlet\'s take a look to ' + outputFile + '\n')