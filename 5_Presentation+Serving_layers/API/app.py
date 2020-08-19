import flask
from flask import request, jsonify
import re

from more_itertools import take

# our Neo4j communication layer
import neo

import redis

import spacy
nlp = spacy.load('ingredients_NER_model')

app = flask.Flask(__name__)
app.config['DEBUG'] = False
app.config['JSON_SORT_KEYS'] = False

@app.route('/', methods = ['GET'])
def root():
    result = {
        'status': 'success',
        'info': 'use the /api endpoint'
    }

    return jsonify(result)

@app.route('/api', methods = ['GET'])
def apiRoot():
    result = {
        'status': 'success'
    }

    return jsonify(result)

@app.route('/api/ingredient/ner', methods = ['GET'])
def ingredientNer():

    # we are expecting the following parameters
    allowedArgs = ['ingredient', 'threshold', 'limit', 'algorithm']
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

        # stripslashes
        args['ingredient'].replace('\\', '')

    else:
        args = request.args
        doc = nlp(args['ingredient'])

        amount = ingredient = ''
        for ent in doc.ents:
            if (ent.label_ == 'AMT'): amount += ent.text + ' '
            if (ent.label_ == 'ING'): ingredient += ent.text + ' '

        amount = amount.strip()
        ingredient = ingredient.strip()

        response = neo.getSimilarIngredients(ingredient, args['threshold'], args['limit'], args['algorithm'])
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'ingredient': args['ingredient'],
                    'query_string': request.query_string.decode()
                },
                'ner': {
                    'amount': amount,
                    'ingredient': ingredient,
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }

    return jsonify(result)

@app.route('/api/ingredients', methods = ['GET'])
def ingredients():

    response = neo.getIngredients()
    
    entities = response['entities']
    query = response['query']

    result = {
        'status': 'success',
        'data': {
            'neo4j': {
                'query': query
            },
            'entities': entities,
        }
    }
    
    return(jsonify(result))

@app.route('/api/recipes/by-ingredients', methods = ['GET'])
def recipesByIngredients():

    # we are expecting the following parameters
    allowedArgs = ['recipename', 'author', 'ingredients', 'threshold', 'limit', 'regionalonly']
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        
        r = redis.Redis(host = 'bigdata2.server', db = 1, port = 6379)
        # let's take a look to the Redis 'cache'
        frequency = redisRecordsExist(r, args['ingredients'])

        # we have to work on the entire graph, it could take time :-/
        limit = False if (not frequency) else args['limit']

        response = neo.getRecipesByIngredients(
            args['recipename'], args['author'], args['ingredients'], args['threshold'], limit, args['regionalonly']
        )
    
        entities = response['entities']

        # delegates to a specific method the computation of the frequencies
        if (not frequency): frequency = frequencyCalc(r, args['ingredients'], entities)
        
        query = response['query']
        limit = args['limit']
        # limits the response to 'limit' results
        entities = entities[:int(limit)]

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'ingredients': args['ingredients'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
                'frequency': {
                    'region': frequency['regions'],
                    'category': frequency['categories'],
                    'level': frequency['levels']
                }
            }
        }
    
    return(jsonify(result))

@app.route('/api/recipes/by-category', methods = ['GET'])
def recipesByCategory():

    # we are expecting the following parameters
    allowedArgs = ['category', 'limit' ]
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesByCategory(args['category'], args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'category': args['category'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))

@app.route('/api/recipes/by-region', methods = ['GET'])
def recipesByRegion():

    # we are expecting the following parameters
    allowedArgs = ['region', 'limit' ]
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesByRegion(args['region'], args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'region': args['region'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))

@app.route('/api/recipes/by-level', methods = ['GET'])
def recipesByLevel():

    # we are expecting the following parameters
    allowedArgs = ['level', 'limit' ]
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesByLevel(args['level'], args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'level': args['level'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))

@app.route('/api/recipes/by-ingredient', methods = ['GET'])
def recipesByIngredient():

    # we are expecting the following parameters
    allowedArgs = ['ingredient', 'limit' ]
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesByIngredient(args['ingredient'], args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'ingredient': args['ingredient'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))       

@app.route('/api/recipes/by-users', methods = ['GET'])
def recipesByUsers():

    # we are expecting the following parameters
    allowedArgs = ['limit' ]
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesByUsers(args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))

@app.route('/api/recipes/by-similarity', methods = ['GET'])
def recipesBySimilarity():

    # we are expecting the following parameters
    allowedArgs = ['id', 'threshold', 'limit']
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:
        args = request.args
        response = neo.getRecipesBySimilarity(args['id'], args['threshold'], args['limit'])
        
        entities = response['entities']
        query = response['query']

        result = {
            'status': 'success',
            'data': {
                'request': {
                    'id': args['id'],
                    'query_string': request.query_string.decode()
                },
                'neo4j': {
                    'query': query
                },
                'entities': entities,
            }
        }
    
    return(jsonify(result))

@app.route('/api/categories', methods = ['GET'])
def categories():

    response = neo.getCategories()
        
    entities = response['entities']
    query = response['query']

    result = {
        'status': 'success',
        'data': {
            'neo4j': {
                'query': query
            },
            'entities': entities,
        }
    }
    
    return(jsonify(result))

@app.route('/api/regions', methods = ['GET'])
def regions():

    response = neo.getRegions()
        
    entities = response['entities']
    query = response['query']

    result = {
        'status': 'success',
        'data': {
            'neo4j': {
                'query': query
            },
            'entities': entities,
        }
    }
    
    return(jsonify(result))

@app.route('/api/levels', methods = ['GET'])
def levels():

    response = neo.getLevels()
        
    entities = response['entities']
    query = response['query']

    result = {
        'status': 'success',
        'data': {
            'neo4j': {
                'query': query
            },
            'entities': entities,
        }
    }
    
    return(jsonify(result))    

@app.route('/api/ingredient/ner-feedback', methods = ['POST'])
def ingredientNerFeedback():

    # we are expecting the following parameters
    allowedArgs = ['raw', 'ingredient', 'amount']
    if (set(allowedArgs) != set(request.args)):
        result = {
            'status': 'fail',
            'query_string': request.query_string.decode()
        }

    else:

        args = request.args

        # stripslashes
        args['ingredient'].replace('\\', '')
        args['amount'].replace('\\', '')

        r = redis.Redis(host = 'bigdata2.server', db = 0, port = 6379)    
        # Redis sets: unordered collections of strings
        r.sadd('raw-to-ingredient:' + args['raw'], args['ingredient'])
        r.sadd('raw-to-amount:' + args['raw'], args['amount'])

    result = {
        'status': 'success',
        'data': {
            'raw': args['raw'],
            'ingredient': args['ingredient'],
            'amount': args['amount']
        }
    }

    return jsonify(result)

# redisKey == comma separated list of ingredients
def redisRecordsExist(r, redisKey):
    
    # alphabetical order
    redisKey = ','.join(sorted(redisKey.split(','), key=lambda x: x.split()[0]))

    regions = r.hgetall(redisKey + ':regions')
    if (not regions): return False

    categories = r.hgetall(redisKey + ':categories')
    if (not categories): return False

    levels = r.hgetall(redisKey + ':levels')
    if (not levels): return False

    response = { 'regions': regions, 'categories': categories, 'levels': levels }
    # decodes from bytes into utf-8
    for x in response:
        response[x] = { y.decode('utf-8'): response[x].get(y).decode('utf-8') for y in response[x].keys() } 

    return response

def frequencyCalc(r, ingredients, entities):

    # alphabetical order
    redisKey = ingredients
    redisKey = ','.join(sorted(redisKey.split(','), key=lambda x: x.split()[0]))

    ### 1. regions
    regions = {}
    for entity in entities:
        for region in entity['regions']:
            if (len(region) == 0): continue
            try:
                regions[region].append(entity['score'])
            except:
                regions[region] = list()
                regions[region].append(entity['score'])

    overallTot = 0
    for region in regions:
        partialTot = 0
        for score in regions[region]:
            partialTot += score
        overallTot += partialTot / len(regions[region])
        regions[region] = partialTot / len(regions[region])

    for i in regions:
        regions[i] = round(regions[i] * 100 / overallTot, 2)

    regions = dict(sorted(regions.items(), key = lambda x: x[1], reverse = True)[:5])

    r.hmset(redisKey + ':regions', regions)

    ### 2. categories
    categories = {}
    for entity in entities:
        if (len(entity['category']) == 0): continue
        try:
            categories[entity['category']].append(entity['score'])
        except:
            categories[entity['category']] = list()
            categories[entity['category']].append(entity['score'])
    overallTot = 0

    for category in categories:
        partialTot = 0
        for score in categories[category]:
            partialTot += score
        overallTot += partialTot / len(categories[category])
        categories[category] = partialTot / len(categories[category])

    for i in categories:
        categories[i] = round(categories[i] * 100 / overallTot, 2)

    categories = dict(sorted(categories.items(), key = lambda x: x[1], reverse = True)[:5])
    r.hmset(redisKey + ':categories', categories)

    ### 3. levels
    levels = {}
    for entity in entities:
        if (len(entity['level']) == 0): continue
        try:
            levels[entity['level']].append(entity['score'])
        except:
            levels[entity['level']] = list()
            levels[entity['level']].append(entity['score'])

    for level in levels:
        partialTot = 0
        for score in levels[level]:
            partialTot += score
        overallTot += partialTot / len(levels[level])
        levels[level] = partialTot / len(levels[level])

    for i in levels:
        levels[i] = round(levels[i] * 100 / overallTot, 2)

    levels = dict(sorted(levels.items(), key = lambda x: x[1], reverse = True))
    r.hmset(redisKey + ':levels', levels)

    return { 'regions': regions, 'categories': categories, 'levels': levels }



if __name__ == '__main__':
    app.run(host = '0.0.0.0')