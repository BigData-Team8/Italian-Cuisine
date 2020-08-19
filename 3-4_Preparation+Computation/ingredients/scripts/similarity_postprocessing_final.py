import json
import os, sys
import redis

import nltk
from nltk.metrics import *

import pandas as pd

csv = 'ingredients_final-groupby.csv'
df = pd.read_csv(csv, usecols = ['Final', 'Freq', 'Freq_Cucchiaio', 'Freq_GZ', 'Freq_RR' ])
df = df.sort_values(by = ['Final'], ascending = True)

result = {}
i = 0

for indexS, rowS in df.iterrows(): 
    sourceIng = rowS['Final']
    sourceFreq = rowS['Freq']

    if (sourceFreq >= 3):

	    i += 1
	    # print(i, sourceIng, sourceFreq)

	    # for key in result:
	    	# print(key, result[key])

	    for indexD, rowD in df.iterrows():
	    	destIng = rowD['Final']
	    	destFreq = rowD['Freq']

	    	if (sourceIng != destIng):
	    		distance = edit_distance(sourceIng, destIng)

	    		# https://stackoverflow.com/questions/45783385/normalizing-the-edit-distance
	    		normalizedDistance = distance / max(len(sourceIng), len(destIng))

	    		if (normalizedDistance < 0.2 ):

	    			# in this case the frequency of the source ingredient is higher than the frequency of the destination one
	    			if (sourceFreq > destFreq):
	    				result[destIng] = sourceIng

	    			elif (sourceFreq < destFreq):
	    				result[sourceIng] = destIng

	    			# equals
	    			else:
	    				result[destIng] = sourceIng
	    				
	    			print(sourceIng, '(', sourceFreq, ') => ', destIng, '(', destFreq, ') | distance = ', normalizedDistance)
