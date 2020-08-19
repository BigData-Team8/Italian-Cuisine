import json
import os, sys
import redis

import nltk
import pandas as pd
"""
from IPython.display import display
"""
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 10000)

# from __future__ import print_function
from nltk.metrics import *

csv = 'ingredients_freq-complete.csv'
df = pd.read_csv(csv, usecols = ['Ingredient', 'Freq', 'Freq_Cucchiaio', 'Freq_GZ', 'Freq_RR' ])
df = df.sort_values(by = ['Ingredient'], ascending = False)

result = {}
i = 0

for indexS, rowS in df.iterrows(): 
    sourceIng = rowS['Ingredient']
    sourceFreq = rowS['Freq']

    if (sourceFreq == 1):

	    i += 1
	    # print(i, sourceIng, sourceFreq)

	    # for key in result:
	    	# print(key, result[key])

	    for indexD, rowD in df.iterrows():
	    	destIng = rowD['Ingredient']
	    	destFreq = rowD['Freq']

	    	if (sourceIng != destIng):
	    		distance = edit_distance(sourceIng, destIng)

	    		# https://stackoverflow.com/questions/45783385/normalizing-the-edit-distance
	    		normalizedDistance = distance / max(len(sourceIng), len(destIng))

	    		if (normalizedDistance < 0.15 ):

	    			# in this case the frequency of the source ingredient is higher than the frequency of the destination one
	    			if (sourceFreq > destFreq):
	    				result[destIng] = sourceIng

	    			elif (sourceFreq < destFreq):
	    				result[sourceIng] = destIng

	    			# equals
	    			else:
	    				result[destIng] = sourceIng
	    				
	    			print(sourceIng, '(', sourceFreq, ') => ', destIng, '(', destFreq, ') | distance = ', normalizedDistance)

