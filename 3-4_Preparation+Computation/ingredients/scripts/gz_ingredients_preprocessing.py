"""
the aim of this program is to refine the list of ingredients provided by Giallo Zafferano
"""

import os
import json
import sys

import re

import redis

import spacy
nlp = spacy.load('it_core_news_sm')

GZ_inputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/gz_ingredients_ORIG'

# do we need to remove italian stopwords?
# spacy_stopwords = spacy.lang.it.stop_words.STOP_WORDS
# print(spacy_stopwords)

# use 'SELECT 2' in order to select the current DB
r = redis.Redis(db = 2, port = 6310)

# strip everything after one of the following keywords
endingTokens = [ 
				' oppure ', 	# 80 g di burro oppure strutto
				' per ',		# 16 g di lievito in polvere per dolci senza glutine
				' in ',			# 1 GZ abbondante di cannella in polvere
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

	affectedLines = 0

	with open(GZ_inputFile) as f:
		totRows = sum(1 for _ in f)

	# cleaning pipeline
	with open(GZ_inputFile) as f:

		for line in f:
			orig = line.strip('\n')
			# the pre processing is indiscriminately applied to all the ingredients
			line = preProcessingCleaning(line)
			if (line != orig):
				affectedLines += 1
			print(line)

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

	# 5. add the key-value pair into Redis
	# https://stackoverflow.com/questions/21768017/how-to-reverse-lookup-in-redis
	r.set('GZ:orig:' + orig, line)
	# we invert, also, the key-pair value for reverse lookup
	r.set('GZ:1st:' + line, orig)

	return line

# let's start ;-)
if __name__ == '__main__':
    main()