import json
import os, sys
import redis

import pandas as pd
"""
from IPython.display import display
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 10000)
"""

r1 = redis.Redis(db = 1, port = 6310)
r2 = redis.Redis(db = 2, port = 6310)
# GZ
r3 = redis.Redis(db = 3, port = 6310)

inputFileCucchiaio = 'cucchiaio.json'
inputFileGZ = 'giallo_zafferano.json'

ingDict = {}

csvList = []

def main():

    print('working on Cucchiaio')
    with open(inputFileCucchiaio) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:

        i += 1
        print(i, ' working on ', node['url'])

        for ingredient in node['ingredients']:

            nodeDict = {}
            nodeDict['source'] = 'cucchiaio'
            nodeDict['url'] = node['url']
            nodeDict['title'] = node['main']['title']
            nodeDict['ORIG_ing'] = ingredient

            nodeDict['PRE_ing'] = ''
            nodeDict['NER_ing'] = ''
            nodeDict['POST_ing'] = ''

            pre = r1.get('cucchiaio:orig-to-pre:' + ingredient)
            if (pre):
                pre = pre.decode('utf-8')

                nodeDict['PRE_ing'] = pre

                ner = r1.get('cucchiaio:pre-to-ner-ingredient:' + pre)
                if (ner):
                    ner = ner.decode('utf-8')

                    nodeDict['NER_ing'] = ner

                    last = r2.get('cucchiaio:ner-ingredient-to-hand:' + ner)
                    if (last):
                        last = last.decode('utf-8')

                        nodeDict['POST_ing'] = last

                        # print('\n' + ingredient + '\n\t' + pre + '\n\t' + ner + '\n\t' + last)

                        try:
                            ingDict[last]['freq'] += 1
                        except:
                            ingDict[last] = {}
                            ingDict[last]['freq'] = 1
                            
                        try:
                            ingDict[last]['freq_cucchiaio'] += 1
                        except:
                            ingDict[last]['freq_cucchiaio'] = 1

            csvList.append(nodeDict)

    df = pd.DataFrame(csvList)

    display(df)

    df.to_csv('cucchiaio_ingredients.csv')

    exit()



    print('working on GZ')
    with open(inputFileGZ) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:

        for ingredient in node['ingredients']:

            # print(ingredient)

            last = r3.get('gz:orig-ingredient-to-hand:' + ingredient)
            if (last):
                last = last.decode('utf-8')

                try:
                    ingDict[last]['freq'] += 1
                except:
                    ingDict[last] = {}
                    ingDict[last]['freq'] = 1
                    
                try:
                    ingDict[last]['freq_GZ'] += 1
                except:                    
                    ingDict[last]['freq_GZ'] = 1

    rows = []
    for ing in ingDict:
        row = {}
        nestedDict = ingDict[ing]
        
        try:
            freq_cucchiaio = nestedDict['freq_cucchiaio']
        except:
            freq_cucchiaio = 0
        
        try:
            freq_GZ = nestedDict['freq_GZ']
        except:
            freq_GZ = 0
        
        row['Ingredient'] = ing
        row['Freq'] = nestedDict['freq']
        row['Freq_Cucchiaio'] = freq_cucchiaio
        row['Freq_GZ'] = freq_GZ
        
        rows.append(row)

    for row in rows:
        print(row)

    # df = pd.DataFrame(rows)
    
    # display(df)
    
    """
    df = pd.DataFrame(ingDict.items(), columns=['Ingredient', 'Freq'])
    df.sort_values(by = ['Freq'], inplace = True, ascending = False)
    """
    
    """
    df.to_csv('cucchiaio_freq-1.csv')
    df.sort_values(by = ['Ingredient'], inplace = True)    
    df.to_csv('cucchiaio_freq-2.csv')
    """
    
# let's start ;-)
if __name__ == '__main__':
    main()