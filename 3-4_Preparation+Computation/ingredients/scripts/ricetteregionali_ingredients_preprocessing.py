"""
the aim of this program is to create a list of ingredients ready for ML

1. we first apply a kind of preprocessing in order to fix/remove the most "visible" problems
2. we generate a CoNLL syntax of all Cucchiaio ingredients, useful for refeining the preliminar tagging result by hand
"""

import os
import json
import sys

import re

import redis

import spacy
nlp = spacy.load('it_core_news_sm')

inputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/ricetteregionali_ingredients_ORIG_unique_sort'

# do we need to remove italian stopwords?
# spacy_stopwords = spacy.lang.it.stop_words.STOP_WORDS
# print(spacy_stopwords)

# use 'SELECT 2' in order to select the current DB
r = redis.Redis(db = 6, port = 6310)

preProcessingRules = {
	'replace': {

		'startsWith': { 'NULL': 'NULL' },

		'endsWith': { 'NULL': 'NULL' },

		'everywhere': { 'NULL': 'NULL' },

		# exact matching
		'equals': { 'NULL': 'NULL' }
	},

	'remove': {
			'equals': [ 'NULL' ],
			'startsWith': [ 'NULL' ]	
	}
}

# strip everything after one of the following keywords
endingTokens = [ 
				' oppure ', 	# 80 g di burro oppure strutto
				' per ',		# 16 g di lievito in polvere per dolci senza glutine
				' in ',			# 1 cucchiaio abbondante di cannella in polvere
				' già ',		# 400 g di ceci già lessati
				' a ',			# 1 tuorlo a temperatura ambiente
				' più ',		# 100 g di lamponi più quelli per il decoro
				' senza ',		# 450 g di fontina o fontal senza crosta
				' + ',			# 200 g di panna fresca + 3 cucchiai
				' dello ',		# 6 tranci di focaccia di pane dello spessore di circa due centimetri
				' delle ',		# 1 baguette di pane delle stesse dimensioni del filetto
				' di circa ',	# 1 cuore di lattuga di circa 200 g
				' non ',		# 500 g di carote non troppo grosse
				' o ',			# un bicchierino di cognac o whisky o marsala
				' e ',			# cedro e arancia canditi
				' ed '
				]

# adjectives = {}

def main():

	rowCount = 0

	affectedLines = 0	# how many lines (ingredinets) have been modified during the pre processing phase?
	with open(inputFile) as f:
		# number of rows in the input file (the rand file)
		totRows = sum(1 for _ in f)

	# cleaning pipeline
	with open(inputFile) as f:

		for line in f:

			rowCount += 1
			orig = line.lower().strip('\n')

			# the pre processing is indiscriminately applied to all the ingredients
			line = preProcessingCleaning(line)
			if (line is not None):
				print(orig + '\n' + line + '\n')
				if (line != orig): affectedLines += 1

	print(str(affectedLines) + ' over ' + str(totRows) + ' has been modified by the preprocessing phase ')

def preProcessingCleaning(line):
	orig = line.strip('\n')

	# 1. lower case name
	line = line.lower().strip('\n')

	# 2. remove everything in parentheses
	line = re.sub('\(.*?\)','', line)

	# 3. remove all after an ending token
	for token in endingTokens:
		result = line.rsplit(token, 1)

		if (len(result) > 1):
			line = result[0]

	# 4. preprocessing fine-grained rules
	for match in preProcessingRules['replace']['startsWith']:
		rule = preProcessingRules['replace']['startsWith'][match]
		if line.startswith(match): line = line.replace(match, rule, 1)

	for match in preProcessingRules['replace']['endsWith']:
		rule = preProcessingRules['replace']['endsWith'][match]
		if line.endswith(match): line = line.replaceRight(line, match, rule, 1)

	for match in preProcessingRules['replace']['everywhere']:
		rule = preProcessingRules['replace']['everywhere'][match]
		line = line.replace(match, rule)

	for match in preProcessingRules['replace']['equals']:
		rule = preProcessingRules['replace']['equals'][match]
		if (line == match): line = rule

	for match in preProcessingRules['remove']['equals']:
		if (line == match): line = ''

	for match in preProcessingRules['remove']['startsWith']:
		if (line.startswith(match)): line = ''

	# 5. add the key-value pair into Redis
	# https://stackoverflow.com/questions/21768017/how-to-reverse-lookup-in-redis
	r.set('ricetteregionali:orig-to-pre:' + orig, line.strip())

	return line

# let's start ;-)
if __name__ == '__main__':
    main()