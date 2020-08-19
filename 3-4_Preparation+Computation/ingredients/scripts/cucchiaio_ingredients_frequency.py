import json
import os, sys
import redis

r1 = redis.Redis(db = 1, port = 6310)
r2 = redis.Redis(db = 2, port = 6310)

inputFile = os.path.dirname(os.path.realpath(__file__)) + 'cucchiaio.json'

ingDict = {}

def main():

    with open(inputFile) as jsonFile:
        nodes = json.load(jsonFile)

    i = 0

    for node in nodes:

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

                        # print('\n' + ingredient + '\n\t' + pre + '\n\t' + ner + '\n\t' + last)

                        try:
                            ingDict[last] += 1
                        except:
                            ingDict[last] = 1

    for ing in ingDict:
        print(str(ingDict[ing]), ing)

# let's start ;-)
if __name__ == '__main__':
    main()