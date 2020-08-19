import json
import os, sys
import redis

import spacy
nlp = spacy.load('it_core_news_sm')

import pandas as pd

# from IPython.display import display
pd.set_option('display.max_rows', 5000)
pd.set_option('display.max_columns', 5000)
pd.set_option('display.width', 10000)

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

ingDict = {}
tokenFreq = {}

def main():

    cucchiaio_count = 0
    GZ_count = 0
    RR_count = 0
    
    print('working on Cucchiaio')
    with open(inputFileCucchiaio) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:
        
        i += 1
        print(i, 'working on: ', node['url'])

        for ingredient in node['ingredients']:
            
            pre = r1.get('cucchiaio:orig-to-pre:' + ingredient)
            if (pre):
                pre = pre.decode('utf-8')
                ner = r1.get('cucchiaio:pre-to-ner-ingredient:' + pre)
                if (ner):
                    ner = ner.decode('utf-8')
                    last = r2.get('cucchiaio:ner-ingredient-to-hand:' + ner)
                    if (last):
                        last = last.decode('utf-8')
                        
                        """
                        do we also need word frequencies?

                        doc = nlp(last)
                        for token in doc:
                            try: 
                                tokenFreq[token.text.lower().strip()] += 1
                            except:
                                tokenFreq[token.text.lower().strip()] = 1  
                        """

                        # print('\n' + ingredient + '\n\t' + pre + '\n\t' + ner + '\n\t' + last)

                        # cucchiaio_count += 1
                        
                        try:
                            ingDict[last]['freq'] += 1
                        except:
                            ingDict[last] = {}
                            ingDict[last]['freq'] = 1
                            
                        try:
                            ingDict[last]['freq_cucchiaio'] += 1
                        except:
                            ingDict[last]['freq_cucchiaio'] = 1

    
    for ing in ingDict:
        cucchiaio_count += 1
    


    print('working on GZ')
    with open(inputFileGZ) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:
        
        i += 1
        print(i, 'working on: ', node['url'])
        
        for ingredient in node['ingredients']:

            # print(ingredient)

            last = r3.get('gz:orig-ingredient-to-hand:' + ingredient)
            if (last):
                last = last.decode('utf-8')
                
                """
                doc = nlp(last)
                for token in doc:
                    try: 
                        tokenFreq[token.text.lower().strip()] += 1
                    except:
                        tokenFreq[token.text.lower().strip()] = 1                
                """

                # GZ_count += 1
                
                try:
                    ingDict[last]['freq'] += 1
                except:
                    ingDict[last] = {}
                    ingDict[last]['freq'] = 1
                    
                try:
                    ingDict[last]['freq_GZ'] += 1
                except:                    
                    ingDict[last]['freq_GZ'] = 1

    totRows = 0
    for ing in ingDict:
        totRows += 1
    GZ_count = totRows - cucchiaio_count
    


    print('working on RicetteRegionali')
    with open(inputFileRR) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:
        
        i += 1
        print(i, 'working on: ', node['url'])
        
        for ingredient in node['ingredients']:

            ingredient = ingredient.strip('\n').strip().lower()

            pre = r5.get('ricetteregionali:orig-to-pre:' + ingredient)
            if (not pre): pre = r6.get('ricetteregionali:orig-to-pre:' + ingredient)

            if (pre):
                pre = pre.decode('utf-8')

                last = r5.get('ricetteregionali:pre-ingredient-to-ner+hand:' + pre)
                if (not last): last = r6.get('ricetteregionali:pre-ingredient-to-ner+hand:' + pre)

                if (last):
                    last = last.decode('utf-8')

                    # RR_count += 1
                    
                    try:
                        ingDict[last]['freq'] += 1
                    except:
                        ingDict[last] = {}
                        ingDict[last]['freq'] = 1
                        
                    try:
                        ingDict[last]['freq_RR'] += 1
                    except:                    
                        ingDict[last]['freq_RR'] = 1
                else:
                    print('Orphan LAST: ', ingredient)
            else:
                print('Orphan PRE: ', ingredient)

    totRows = 0
    for ing in ingDict:
        totRows += 1
    RR_count = totRows - cucchiaio_count - GZ_count
        


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
        
        try:
            freq_RR = nestedDict['freq_RR']
        except:
            freq_RR = 0
        
        row['Ingredient'] = ing
        row['Freq'] = nestedDict['freq']
        row['Freq_Cucchiaio'] = freq_cucchiaio
        row['Freq_GZ'] = freq_GZ
        row['Freq_RR'] = freq_RR
        
        rows.append(row)



    """
    for row in rows:
        print(row)
    """
    df = pd.DataFrame(rows)
    df = df.sort_values(by = ['Ingredient'], ascending = True)
    df.to_csv('ingredients_freq-complete.csv')
    # display(df)
    
    print('cucchiaio_count: ', cucchiaio_count)
    print('GZ_count: ', GZ_count)
    print('RR_count: ', RR_count)
        
# let's start ;-)
if __name__ == '__main__':
    main()