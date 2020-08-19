"""
all the details about this script, the CUD format, the Kafka-Neo4j integration
https://neo4j.com/docs/labs/neo4j-streams/current/consumer/#_cud_file_format
"""

import os
import json
from bson import json_util
import sys

from kafka import KafkaConsumer
from kafka import KafkaProducer

import threading

# some configuration parameters
params = {
	'kafkaHost': 'bigdata1.server',
	'kafkaPort': '9092',
	'consumerTopicName': 'datasets',
	'producerTopicName': 'datasets_CUD',
	'groupId': 'datasets_CUD',
	'numWorkerThreads': 1
}

threads = []

# iterates over the folder processing every html file inside it
def main():

	for i in range(params['numWorkerThreads']):
	    t = threading.Thread(target = worker)
	    t.start()
	    threads.append(t)

def worker():

	recipeIds = []

	consumer = kafkaConsumer()
	producer = kafkaProducer()

	for msg in consumer:
		# gets the 'payload' of the Kafka's message
		record = json.loads(msg.value, encoding = 'utf-8')
		# print(json.dumps(record, indent = 2, ensure_ascii = False))

		### RECIPE
		if (record['main']['Author'] == 'giallozafferano.it'):
			CUD = createGZRecipeNode(record)
			recipeId = CUD['properties']['url']
		if (record['main']['Author'] == 'cucchiaio.it'):
			CUD = createCucchiaioRecipeNode(record)
			recipeId = CUD['properties']['url']
		if (record['main']['Author'] == 'ricetteregionali.net'):
			CUD = createRRRecipeNode(record)
			recipeId = CUD['properties']['url']

		# skips eventual redundant URLs / recipes; yes we have! We discovered them because of Neo4j ;-)
		if (recipeId not in recipeIds): 
			recipeIds.append(recipeId)
			produceContent(producer, CUD)
		else:
			continue

		### CATEGORY
		"""
		we preferred to model the category as an attribute instead of a node-entity

		for categoryName in record['main']['type']:
			produceContent(producer, createCategoryNode(categoryName))
			produceContent(producer, createHasCategoryRelation(recipeId, categoryName))
		"""
		
		### INGREDIENT
		for ingredientName in record['ingredients_def']:
			produceContent(producer, createIngredientNode(ingredientName))
			produceContent(producer, createHasIngredientRelation(recipeId, ingredientName))

		### REGION
		for regionName in record['main']['regionality']:
			produceContent(producer, createRegionNode(regionName))
			produceContent(producer, createRegionalityRelation(recipeId, regionName))

		### NATION
		for nationName in record['main']['nationality']:
			produceContent(producer, createNationNode(nationName))
			produceContent(producer, createNationalityRelation(recipeId, nationName))

		### AUTHOR
		authorName = record['main']['Author']
		produceContent(producer, createAuthorNode(authorName))
		produceContent(producer, createWrittenByRelation(recipeId, authorName))

	consumer.close()

def createGZRecipeNode(inRecord):

	recipeId = inRecord['url']

	# in the json source file here we have an array
	try: category = inRecord['main']['type'][0]
	except: category = ''

	# in the json source file here we have an array
	try: kcal = inRecord['main']['kcal'][0]
	except: kcal = ''

	try: image = inRecord['main']['image']
	except: image = ''

	try: description = inRecord['main']['description']
	except: description = ''

	print('creating GZ recipe node', recipeId)

	return {
		'op': 'merge',
		'properties': {
			'url': recipeId,
			'title': inRecord['main']['title'],
			'category': category,
			'level': inRecord['main']['Level'],
			'score': inRecord['main']['score'],
			'reviews': inRecord['main']['reviews'],
			'kcal': kcal,
			'author': inRecord['main']['Author'],
			'image': image,
			'description': description
		},
		'ids': {
			'id': recipeId,
		},
		'labels': ['Recipe'],
		'type': 'node',
		'detach': 'true'
	}

def createCucchiaioRecipeNode(inRecord):

	recipeId = inRecord['main']['url']

	# in the json source file here we have an array
	try: category = inRecord['main']['type'][0]
	except: category = ''

	try: image = inRecord['main']['image']
	except: image = ''

	try: description = inRecord['main']['description']
	except: description = ''

	print('creating Cucchiaio recipe node', recipeId)

	return {
		'op': 'merge',
		'properties': {
			'url': recipeId,
			'title': inRecord['main']['title'],
			'category': category,
			'level': inRecord['main']['Level'],
			'author': inRecord['main']['Author'],
			'image': image,
			'description': description			
		},
		'ids': {
			'id': recipeId,
		},
		'labels': ['Recipe'],
		'type': 'node',
		'detach': 'true'
	}

	return recipeId

def createRRRecipeNode(inRecord):

	recipeId = inRecord['url']

	# in the json source file here we have an array
	try: category = inRecord['main']['type'][0]
	except: category = ''

	try: image = inRecord['main']['image']
	except: image = ''

	try: description = inRecord['main']['description']
	except: description = ''

	print('creating RR recipe node', recipeId)

	return {
		'op': 'merge',
		'properties': {
			'url': recipeId,
			'title': inRecord['main']['title'],
			'category': category,
			'level': inRecord['main']['Level'],
			'author': inRecord['main']['Author'],
			'image': image,
			'description': description			
		},
		'ids': {
			'id': recipeId,
		},
		'labels': ['Recipe'],
		'type': 'node',
		'detach': 'true'
	}

	return recipeId

def createIngredientNode(ingredientName):

	print('creating ingredient', ingredientName)

	return {
		'op': 'merge',
		'properties': {
			'name': ingredientName
		},
		'ids': {
			'id': ingredientName
		},
		'labels': ['Ingredient'],
		'type': 'node',
		'detach': 'true'
	}

def createCategoryNode(categoryName):

	print('creating category', categoryName)

	return {
		'op': 'merge',
		'properties': {
			'name': categoryName
		},
		'ids': {
			'id': categoryName
		},
		'labels': ['Category'],
		'type': 'node',
		'detach': 'true'
	}

def createRegionNode(regionName):

	print('creating region', regionName)

	return {
		'op': 'merge',
		'properties': {
			'name': regionName
		},
		'ids': {
			'id': regionName
		},
		'labels': ['Region'],
		'type': 'node',
		'detach': 'true'
	}

def createNationNode(nationName):

	print('creating nation', nationName)

	return {
		'op': 'merge',
		'properties': {
			'name': nationName
		},
		'ids': {
			'id': nationName,
		},
		'labels': ['Nation'],
		'type': 'node',
		'detach': 'true'
	}

def createAuthorNode(authorName):

	print('creating author', authorName)

	return {
		'op': 'merge',
		'properties': {
			'name': authorName
		},
		'ids': {
			'id': authorName,
		},
		'labels': ['Author'],
		'type': 'node',
		'detach': 'true'
	}

def createHasCategoryRelation(recipeId, categoryName):

	print('creating HAS_CATEGORY', recipeId, categoryName)

	return {
		'op': 'create',
		'rel_type': 'HAS_CATEGORY',
		'properties': {
			'foo': 'bar'
		},
		'from': {
			'ids': { 'id': recipeId },
			'labels': ['Recipe']
		},
		'to': {
			'ids': { 'name': categoryName },
			'labels': ['Category']
		},
		'type':'relationship'
	}

def createHasIngredientRelation(recipeId, ingredientName):

	print('creating HAS_INGREDIENT', recipeId, ingredientName)

	return {
		'op': 'create',
		'rel_type': 'HAS_INGREDIENT',
		'properties': {
			'foo': 'bar'
		},
		'from': {
			'ids': { 'id': recipeId },
			'labels': ['Recipe']
		},
		'to': {
			'ids': { 'name': ingredientName },
			'labels': ['Ingredient']
		},
		'type':'relationship'
	}

def createRegionalityRelation(recipeId, regionName):

	print('creating REGIONALITY', recipeId, regionName)

	return {
		'op': 'create',
		'rel_type': 'REGIONALITY',
		'properties': {
			'foo': 'bar'
		},
		'from': {
			'ids': { 'id': recipeId },
			'labels': ['Recipe']
		},
		'to': {
			'ids': { 'name': regionName },
			'labels': ['Region']
		},
		'type':'relationship'
	}

def createNationalityRelation(recipeId, nationName):

	print('creating NATIONALITY', recipeId, nationName)

	return {
		'op': 'create',
		'rel_type': 'NATIONALITY',
		'properties': {
			'foo': 'bar'
		},
		'from': {
			'ids': { 'id': recipeId },
			'labels': ['Recipe']
		},
		'to': {
			'ids': { 'name': nationName },
			'labels': ['Nation']
		},
		'type':'relationship'
	}

def createWrittenByRelation(recipeId, authorName):

	print('creating WRITTEN_BY', recipeId, authorName)

	return {
		'op': 'create',
		'rel_type': 'WRITTEN_BY',
		'properties': {
			'foo': 'bar'
		},
		'from': {
			'ids': { 'id': recipeId },
			'labels': ['Recipe']
		},
		'to': {
			'ids': { 'name': authorName },
			'labels': ['Author']
		},
		'type':'relationship'
	}

# kafka-python consumer instance
def kafkaConsumer():
    consumer = KafkaConsumer(params['consumerTopicName'],
		bootstrap_servers = params['kafkaHost'] + ':' + params['kafkaPort'],
		auto_offset_reset = 'earliest',
		enable_auto_commit = False,
		api_version = (0, 10),
		group_id = params['groupId'],
		consumer_timeout_ms = 40000)

    return consumer

# kafka-python producer instance
def kafkaProducer():
	producer = KafkaProducer(
        bootstrap_servers = [params['kafkaHost'] + ':' + params['kafkaPort']],
        api_version = (0, 10))

	return producer

def jsonDump(ds):
	print(json.dumps(ds, indent = 2, ensure_ascii = False))

def produceContent(producer, data):
	# for testing purposes only
	# print(json.dumps(data, indent = 2, ensure_ascii = False))

	# as discussed here https://stackoverflow.com/questions/31823392/how-to-send-json-object-to-kafka-from-python-client
	# it seems important to encode the json in utf-8
	data = json.dumps(data, default = json_util.default).encode('utf-8')

	try:
		producer.send(params['producerTopicName'], value = data)
		producer.flush()
		print('Message published successfully')

	except Exception as ex:
		print('Exception in publishing message')
		print(str(ex))

# let's start ;-)
if __name__ == '__main__':
    main()