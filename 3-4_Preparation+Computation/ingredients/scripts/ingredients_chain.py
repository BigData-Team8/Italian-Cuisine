import json
import os, sys
import redis

import pandas as pd

# from IPython.display import display
"""
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 10000)
"""

# Cucchiaio
r1 = redis.Redis(db = 1, port = 6310)
r2 = redis.Redis(db = 2, port = 6310)
# GZ
r3 = redis.Redis(db = 3, port = 6310)
# RicetteRegionali
r5 = redis.Redis(db = 5, port = 6310)
r6 = redis.Redis(db = 6, port = 6310)

inputFileCucchiaio = 'cucchiaio.json'
inputFileGZ = 'giallo_zafferano.json'
inputFileRR = 'ricetteregionali.json'

minFreqThreshold = 2



def main():

    csv = 'ingredients_def.csv'
    # df = pd.read_csv(csv, usecols = ['Ingredient', 'Freq', 'Freq_Cucchiaio', 'Freq_GZ', 'Freq_RR', 'Clue', 'Final', 'Def'])
    df = pd.read_csv(csv, usecols = ['Ingredient', 'Clue', 'Def'])
    df = df.sort_values(by = ['Def'], ascending = True)
    ingDict = df.set_index('Ingredient').T.to_dict('list')

    csv = 'ingredients_def-groupby.csv'
    df = pd.read_csv(csv, usecols = ['Def', 'Freq'])
    df = df.sort_values(by = ['Def'], ascending = True)
    ingDict_grouped = df.set_index('Def').T.to_dict('list')

    cucchiaio(ingDict, ingDict_grouped)
    GZ(ingDict, ingDict_grouped)
    RR(ingDict, ingDict_grouped)



def cucchiaio(ingDict, ingDict_grouped):

    print('working on Cucchiaio')
    with open(inputFileCucchiaio) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0
    chain = {}
    nodesDef = []

    for node in nodes:
        
        i += 1
        nodeDefIngredients = []
        print(i, 'working on: ', node['url'])

        for ingredient in node['ingredients']:
            
            chain[ingredient] = {
                'pre': '',
                'ner-ingredient': '',
                'ner-amount': '',
                'post': '',
                'clue': '',
                'def': '',
                'freq': ''
            }

            pre = r1.get('cucchiaio:orig-to-pre:' + ingredient)

            if (pre):
            
                pre = pre.decode('utf-8')
                chain[ingredient]['pre'] = pre
                ner_ingredient = r1.get('cucchiaio:pre-to-ner-ingredient:' + pre)
                ner_amount = r1.get('cucchiaio:pre-to-ner-amount:' + pre)
            
                if (ner_ingredient):
                    
                    ner_ingredient = ner_ingredient.decode('utf-8')
                    chain[ingredient]['ner-ingredient'] = ner_ingredient
                    post = r2.get('cucchiaio:ner-ingredient-to-hand:' + ner_ingredient)

                    if (post):
                        post = post.decode('utf-8')
                        chain[ingredient]['post'] = post
                        
                        chain[ingredient]['clue'] = ingDict[post][0]
                        chain[ingredient]['def'] = ingDict[post][1]

                        def_ = ingDict[post][1]
                        chain[ingredient]['freq'] = ingDict_grouped[def_][0]

                if (ner_amount): chain[ingredient]['ner-amount'] = ner_amount.decode('utf-8')



                # json updating
                if (chain[ingredient]['freq']):
                    if (chain[ingredient]['freq'] > minFreqThreshold):
                        if (def_ not in nodeDefIngredients):
                            nodeDefIngredients.append(def_)
        node['ingredients_def'] = nodeDefIngredients
        nodesDef.append(node)
            
    # writes to file the updated (and definitely?) json
    fileWriter(nodesDef, '../dataset/cucchiaio-def.json')



    # writes the result of the Cucchiaio's ingredients chain on a csv
    rows = []
    for ing in chain:
        row = {}
        nestedDict = chain[ing]
        
        row['Ingredient'] = ing
        row['Pre-NER'] = nestedDict['pre']
        row['NER-Ingredient'] = nestedDict['ner-ingredient']
        row['NER-Amount'] = nestedDict['ner-amount']
        row['Post-NER'] = nestedDict['post']
        row['Normalization'] = nestedDict['clue']
        row['Def'] = nestedDict['def']
        row['Freq'] = nestedDict['freq']
        
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv('cucchiaio_ingredients_chain.csv')



def GZ(ingDict, ingDict_grouped):
    print('working on GZ')
    with open(inputFileGZ) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0
    chain = {}
    nodesDef = []

    for node in nodes:
        
        i += 1
        nodeDefIngredients = []
        print(i, 'working on: ', node['url'])
        
        for ingredient in node['ingredients']:

            chain[ingredient] = {
                'pre': '',
                'clue': '',
                'def': '',
                'freq': ''
            }

            # here we are naming 'pre' the initial phase of manual skimming
            pre = r3.get('gz:orig-ingredient-to-hand:' + ingredient)
            if (pre):

                pre = pre.decode('utf-8')
                chain[ingredient]['pre'] = pre

                chain[ingredient]['clue'] = ingDict[pre][0]
                chain[ingredient]['del'] = ingDict[pre][1]

                def_ = ingDict[pre][1]
                chain[ingredient]['freq'] = ingDict_grouped[def_][0]                



                # json updating
                if (chain[ingredient]['freq']):
                    if (chain[ingredient]['freq'] > minFreqThreshold):
                        if (def_ not in nodeDefIngredients):
                            nodeDefIngredients.append(def_)

        node['ingredients_def'] = nodeDefIngredients
        nodesDef.append(node)
            
    # writes to file the updated (and definitely?) json
    fileWriter(nodesDef, '../dataset/GZ-def.json')



    # writes the result of the GZ's ingredients chain on a csv
    rows = []
    for ing in chain:
        row = {}
        nestedDict = chain[ing]
        
        row['Ingredient'] = ing
        row['Pre'] = nestedDict['pre']
        row['Normalization'] = nestedDict['clue']
        row['Def'] = nestedDict['def']
        row['Freq'] = nestedDict['freq']
        
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv('GZ_ingredients_chain.csv')



def RR(ingDict, ingDict_grouped):

    print('working on RicetteRegionali')
    with open(inputFileRR) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0
    chain = {}
    nodesDef = []

    for node in nodes:
        
        i += 1
        nodeDefIngredients = []
        print(i, 'working on: ', node['url'])
        
        for ingredient in node['ingredients']:

            ingredient = ingredient.strip('\n').strip().lower()
            chain[ingredient] = {
                'pre-ner': '',
                'ner+post': '',
                'ner-amount': '',
                'clue': '',
                'def': '',
                'freq': ''
            }

            pre = r5.get('ricetteregionali:orig-to-pre:' + ingredient)
            if (not pre): pre = r6.get('ricetteregionali:orig-to-pre:' + ingredient)

            if (pre):
                pre = pre.decode('utf-8')
                chain[ingredient]['pre-ner'] = pre

                post = r5.get('ricetteregionali:pre-ingredient-to-ner+hand:' + pre)
                if (not post): post = r6.get('ricetteregionali:pre-ingredient-to-ner+hand:' + pre)

                ner_amount = r5.get('ricetteregionali:pre-to-ner-amount:' + pre)
                if (not ner_amount): ner_amount = r6.get('ricetteregionali:pre-to-ner-amount:' + pre)

                if (post):
                    post = post.decode('utf-8')
                    chain[ingredient]['ner+post'] = post

                    chain[ingredient]['clue'] = ingDict[post][0]
                    chain[ingredient]['def'] = ingDict[post][1]

                    def_ = ingDict[post][1]
                    chain[ingredient]['freq'] = ingDict_grouped[def_][0]

                if (ner_amount): chain[ingredient]['ner-amount'] = ner_amount.decode('utf-8')



                # json updating
                if (chain[ingredient]['freq']):
                    if (chain[ingredient]['freq'] > minFreqThreshold):
                        if (def_ not in nodeDefIngredients):
                            nodeDefIngredients.append(def_)

        node['ingredients_def'] = nodeDefIngredients
        nodesDef.append(node)
    
    # writes to file the updated (and definitely?) json
    fileWriter(nodesDef, '../dataset/RR-def.json')



    # writes the result of the GZ's ingredients chain on a csv
    rows = []
    for ing in chain:
        row = {}
        nestedDict = chain[ing]
        
        row['Ingredient'] = ing
        row['Pre'] = nestedDict['pre-ner']
        row['NER+Post'] = nestedDict['ner+post']
        row['NER-Amount'] = nestedDict['ner-amount']
        row['Normalization'] = nestedDict['clue']
        row['Def'] = nestedDict['def']
        row['Freq'] = nestedDict['freq']
        
        rows.append(row)

    df = pd.DataFrame(rows)
    df.to_csv('RR_ingredients_chain.csv')



def fileWriter(output, outputFile):
    with open(outputFile, 'a') as outfile:
        json.dump(output, outfile, indent = 2, ensure_ascii = False)

# let's start ;-)
if __name__ == '__main__':
    main()