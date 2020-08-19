import json
import os, sys
import redis

import nltk
from nltk.metrics import *

import pandas as pd

csv = 'ingredients_freq-complete.csv'
df = pd.read_csv(csv, usecols = ['Ingredient', 'Freq', 'Freq_Cucchiaio', 'Freq_GZ', 'Freq_RR' ])
df = df.sort_values(by = ['Ingredient'], ascending = True)

result = {}
i = 0

for indexS, rowS in df.iterrows(): 
    sourceIng = rowS['Ingredient']
    sourceFreq = rowS['Freq']

    result[sourceIng] = {
        'destIng': sourceIng,
        'destFreq': sourceFreq
    }

    if (sourceFreq > 5): continue

    # get first 90% of the characters of the string
    token = sourceIng.split(' ')[0]
    sourceIng_sub = token[0 : round(len(sourceIng) * 90 / 100) ]

    for indexD, rowD in df.iterrows():

        destIng = rowD['Ingredient']
        destFreq = rowD['Freq']

        if (sourceIng == destIng): continue
        if (destFreq < 3): continue
        if (not destIng.startswith(sourceIng_sub)): continue

        # try to get all the tokens starting from the second one
        sourceIng_sub = sourceIng
        try: sourceIng_sub = sourceIng[sourceIng.index(' ') + 1:]
        except: pass

        destIng_sub = destIng
        try: destIng_sub = destIng[destIng.index(' ') + 1:]
        except: pass

        distance = edit_distance(sourceIng_sub, destIng_sub)

        # https://stackoverflow.com/questions/45783385/normalizing-the-edit-distance
        normalizedDistance = distance / max(len(sourceIng_sub), len(destIng_sub))

        """
		distance = edit_distance(sourceIng, destIng)
		normalizedDistance = distance / max(len(sourceIng), len(destIng))
        """

        if (normalizedDistance <= 1):

            if (result[sourceIng]['destFreq'] < destFreq):
                result[sourceIng] = {
                    'destIng': destIng,
                    'destFreq': destFreq
                }

                print(sourceIng, '(', sourceFreq, ') => ', destIng, '(', destFreq, ') | distance = ', normalizedDistance)

newColumn = { }
for ing in result:
#    print(ing)
    newColumn[ing] = result[ing]['destIng']

# print(newColumn)

df['Clue'] = df['Ingredient'].map(newColumn)

csv = 'ingredients_freq-complete+clues.csv'
df.to_csv(csv)