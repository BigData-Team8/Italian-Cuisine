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

# we firstly apply the following Bash command to the list of ingredients (a shuffle!):
# shuf cucchiaio_ingredients > cucchiaio_ingredients_rand
cucchiaio_inputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/cucchiaio_ingredients_rand'

outputFile_CoNLL_training = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/cucchiaio_ingredients_training_set.conll'
outputFile_CoNLL_test = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/cucchiaio_ingredients_test_set.conll'
outFile_CoNLL_training = open(outputFile_CoNLL_training, 'a')
outFile_CoNLL_test = open(outputFile_CoNLL_test, 'a')

# do we need to remove italian stopwords?
# spacy_stopwords = spacy.lang.it.stop_words.STOP_WORDS
# print(spacy_stopwords)

# use 'SELECT 1' in order to select the current DB
r = redis.Redis(db = 1, port = 6310)

preProcessingRules = {
	'replace': {

		'startsWith': { 'NULL': 'NULL' },

		'endsWith': { 'NULL': 'NULL' },

		'everywhere': {
			"\\u2028": '',
			"\\\\u2028": ' ',
			"\\u2028": ' ',
			"\\\\u2028": ' ',				
			"\\xa0": ' ',
			"\\\\xa0": ' ',
			"”": '',
			'’': '\'',
			'½': '1/2',
			'\n': '',
			'fi letto': 'filetto',
			'fi letti': 'filetti',
			'pancarré': 'pancarrè',
			'1⁄4': '1/4',
			'¼': '1/4',
			'!/2': '1/2',
			'  ': ' '
		},

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
				' non '			# 500 g di carote non troppo grosse
				]

# adjectives = {}

def main():

	outputFile = outFile_CoNLL_training
	affectedLines = 0	# how many lines (ingredinets) have been modified during the pre processing phase?
	rowCount = 0		# a simple counter

	with open(cucchiaio_inputFile) as f:
		totRows = sum(1 for _ in f)						# number of rows in the input file (the rand file)

	rowsToSelect = int(round(totRows * (15 / 100)))		# total number of ingredients to select (15% of the total)
	trainingSet = int(round(rowsToSelect * (80 / 100)))	# training set (80%)
	testSet = int(round(rowsToSelect * (20 / 100)))		# test set (20%)		

	# cleaning pipeline
	with open(cucchiaio_inputFile) as f:

		for line in f:

			rowCount += 1
			orig = line.strip('\n')

			# the pre processing is indiscriminately applied to all the ingredients
			line = preProcessingCleaning(line)

			if (line != orig): affectedLines += 1

			# the CoNLL syntax is generated accordingly with the established proportions (training set / test set)
			if (outputFile == outFile_CoNLL_training and rowCount >= trainingSet):
				print(rowCount, trainingSet)
				print(rowCount, outputFile)
				outputFile = outFile_CoNLL_test
				rowCount = 1

			if (outputFile == outFile_CoNLL_test and rowCount >= testSet):
				print(rowCount, testSet)
				print(rowCount, outputFile)
				outputFile = None

			genCoNLL(line, outputFile)

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
	r.set('cucchiaio:orig-to-pre:' + orig, line.strip())
	# we invert, also, the key-pair value for reverse lookup
	# r.set('cucchiaio:pre-to-orig:' + line.strip(), orig)

	return line



def genCoNLL(line, outputFile):

	if (not outputFile): return

	key = ''
	tokens = []
	for token in nlp(line):
		tokens.append(token.text)
		if (token.text != ''):
			key += token.text.strip()

	for token in nlp(line):
		tag = getTag(token, tokens)
		outputFile.write(token.text + '\t' + tag + '\n')

	outputFile.write('\n')

# this function doesn't want to be exaustive; it just produces a basic breadcrumb (CoNLL tagging) in order to be
# refined by hand
# (creation of a CoNLL syntax training-set: just a dirty starting point)
# O = discard the token
# ING = Ingredient
# AMT = Amount (amount + unit of mesurement)
def getTag(token, tokens):

	# formal definition
	# https://nlp.stanford.edu/courses/cs224n/2011/reports/rahul1-kjmiller.pdf

	amounts = [ '-', '/', '1/2', 'un', 'uno', 'due', 'tre', 'mezza', 'mezzo', 'dozzina', 'paio' ]

	units = [ 'g', 'gr', 'kg', 'ml', 'cl', 'dl', 'l', 'cm', 'grammo', 'grammi', 'etto', 'chilo', 'kilo', 'litro', 'litri',
	'pizzico', 'vasetto', 'cucchiaio', 'cucchiai', 'cucchiaini', 'cucchiaino', 'spicchio', 'barattolo', 'noce', 'foglia',
	'foglie', 'disco', 'fettine', 'fettina', 'ciuffo', 'costa', 'spicchio', 'spicchi', 'fetta', 'fette', 'manciata', 'rametto',
	'rametti', 'bicchiere', 'bicchieri', 'bicchierino', 'bicchierini', 'cespi', 'cespo', 'tazza', 'tazze', 'tazzina', 'tazzine',
	'bottiglia', 'bocconcini', 'bocconcino', 'cuori', 'confezione', 'mazzo', 'mazzetto', 'mazzetti', 'busta', 'buste', 'bustina',
	'bustine', 'stecca', 'qb', 'buccia', 'bucce' ]

	descriptions = [
	# size
	'piccolo', 'piccola', 'piccole', 'piccoli', 'medio', 'media', 'medie', 'medi', 'medio-grandi', 'grosso',
	'grossa', 'grosse' 'grossi', 'mezzo', 'mezza', 'spesso', 'spessa', 'spesse', 'spessi',
	'grande', 'grandi', 'media dimensione', 'medie dimensioni', 'sottili', 'sottile', 
	# quality
	'tritati', 'tritato', 'pulito', 'pulita', 'pulite', 'puliti', 'temperatura ambiente', 'non trattato'
	'crudo', 'cruda', 'crude', 'crudi', 'selvatica', 'selvatico', 'rotondo', 'baby', 'maturo', 'matura', 'mature', 'maturi',
	'ramati', 'lessi', 'lesso', 'lessato', 'lessati', 'fresco', 'fresca', 'freschi', 'fresche' ]

	#				'di', 'in'
	prepositions = [ 'a', 'da', 'con', 'su', 'per', 'tra', 'fra' ]
	articles = [ 'il', 'la', 'le', 'lo', 'gli' ]
	misc = [ ]

	# common pattern (e.g.: 250 g di patate)
	# we'd like to intercept the 'di' preposition that, being in that position, is not significant
	if (token.i == 2 and (token.text.lower() == 'di' or token.text.lower() == 'd\'')):
		if (tokens[token.i - 1].isdigit() or (tokens[token.i - 1].lower() in amounts) or
			(tokens[token.i - 1].lower() in units)):
			return 'O'

	if (token.text.isdigit() or (token.text.lower() in amounts)):
		return 'AMT'

	elif (token.text.lower() in units):
		return 'AMT'

	elif (token.text.lower() in descriptions):
		return 'ING'

	elif (token.text.lower() in prepositions):
		return 'ING'

	elif (token.text.lower() in articles):
		return 'ING'

	else:
		return 'ING'

# let's start ;-)
if __name__ == '__main__':
    main()