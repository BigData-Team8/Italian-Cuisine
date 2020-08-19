"""
ricetteregionali.net scraping.
The aim of this program is to interact with Kafka and, at the same time, perform scraping activities;
it consumes raw data coming from Apache Nutch crawling activities and produces semi-structured json encoded data with the
most relevant information.
"""

import os
import json
from bson import json_util
import sys
from lxml import html
from bs4 import BeautifulSoup

from kafka import KafkaConsumer
from kafka import KafkaProducer

import threading

import redis

# some configuration parameters
params = {
	'kafkaHost': 'bigdata2.server',
	'kafkaPort': '9092',
	'consumerTopicName': 'ricetteregionali.net_crawling',
	'producerTopicName': 'ricetteregionali.net_scraping',
	'groupId': 'ricetteregionali_scraping',
	'numWorkerThreads': 10
}

# in case we need a local json file
outputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/ricette_regionali.json'

lock = threading.Lock()
threads = []



def main():

	for i in range(params['numWorkerThreads']):
	    t = threading.Thread(target = worker)
	    t.start()
	    threads.append(t)

# https://stackoverflow.com/questions/40896024/if-you-have-less-consumers-than-partitions-what-happens/40935236
# multithreading and Kafka
# each thread consumes 'rawhtml' and, through the scraper, produces semi-structured json encoded data
def worker():
	consumer = kafkaConsumer()
	producer = kafkaProducer()

	for msg in consumer:

		# gets the "payload" of the Kafka's message
		record = json.loads(msg.value)

		url = str(record['url'])
		url = url.replace('[\'', '').replace('\']', '').strip()
		
		if (not url.endswith('html') or '/amp/' in url):
			pass
		else:

			print(url)

		    # gets an empty data structure prototype that will contain all the scraped content of the current page
			ds = getDataStructurePrototype()
			# set the main identification attribute
			ds['url'] = url.replace('[\'', '').replace('\']', '')

			# deals with escaping sequences
			htmlContent = escapingCleaning(record)

			# let's start with the scraping
			ds = scraper(ds, htmlContent)

			# print(ds)

			# pushes the scraping json result to a Kafka brokers cluster
			produceContent(producer, ds)

			# writes to local file
			if (ds): fileWriter(ds)

	consumer.close()

# very basic cleaning activities
def escapingCleaning(record):
	# 1. raw HTML extraction and string casting
	htmlContent = str(record['rawhtml'])
	# 2. escaping sequences manager
	return htmlContent.replace('\\n', ' ').replace('\\"', '"').replace('\\t', ' ').replace("\\'", "'")

# kafka-python consumer instance
def kafkaConsumer():
    consumer = KafkaConsumer(params['consumerTopicName'],
		bootstrap_servers = params['kafkaHost'] + ':' + params['kafkaPort'],
		auto_offset_reset = 'earliest',

		# pay particular attention to this parameter
		enable_auto_commit = True,
		
		api_version = (0, 10),
		group_id = params['groupId'],
		consumer_timeout_ms = 100000)

    return consumer

# kafka-python producer instance
def kafkaProducer():
	producer = KafkaProducer(
        bootstrap_servers = [params['kafkaHost'] + ':' + params['kafkaPort']],
        api_version = (0, 10))

	return producer

def produceContent(producer, data):
	# for testing purposes only
	# print(json.dumps(data, indent = 2, ensure_ascii = False))

	# as discussed here https://stackoverflow.com/questions/31823392/how-to-send-json-object-to-kafka-from-python-client
	# it seems important to encode the json in utf-8
	data = json.dumps(data, default = json_util.default).encode('utf-8')

	try:
		producer.send(params['producerTopicName'], value = data)
		producer.flush()
		# print('Message published successfully')(|)

	except Exception as ex:
		print('Exception in publishing message')
		print(str(ex))

def scraper(ds, htmlContent):

	soup = BeautifulSoup(htmlContent, 'lxml')

	# scraping activities
	mainInfoScraper(soup, ds)
	metaTagScraper(soup, ds)
	ingredientsScraper(soup, ds)

	if (not ds['ingredients']):
		return None

	tagsScraper(soup, ds)
	featuresScraper(soup, ds)

	return ds

def tagsScraper(soup, ds):
	try:
		tags = []
		for elm in soup.find('div', {'class': 'details-tags'}).find('ul').findAll('li'):
			tags.append(elm.select('a')[0].text)

		if (tags): ds['main']['tags'] = tags

	except Exception as e:
		pass

def mainInfoScraper(soup, ds):
	try:
		category = soup.find('ul', {'class': 'recipe-specs'}).select('span')[2].text
		ds['main']['category'] = category
	except Exception as e:
		pass

	try:
		region = soup.find('div', {'id': 'menuNavigazione'}).select('li')[4].select('span')[0].text
		ds['main']['region'] = region
	except Exception as e:
		pass

def featuresScraper(soup, ds):

	try:
		difficulty = soup.find('ul', {'class': 'recipe-specs'}).select('span')[4].text
		ds['features']['difficulty'] = difficulty
	except Exception as e:
		pass

# extracts all useful metatags
def metaTagScraper(soup, ds):
	# extracts the page title from meta property tag
	elm = soup.find('meta', property = 'og:title')
	# if (elm): ds['metatag']['og']['title'] = elm.attrs['content']
	if (elm): ds['main']['title'] = elm.attrs['content']

	# extracts the page urls from meta property tag
	elm = soup.find('meta', property = 'og:url')
	if (elm): ds['main']['url_meta'] = elm.attrs['content']

	# extracts the 'description' metatag
	elm = soup.find('meta', attrs = {'name': 'Description'})
	if (elm): ds['main']['description'] = elm.attrs['content']
	
	# extracts the 'image' metatag
	elm = soup.find('meta', property = 'og:image')
	if (elm): ds['main']['image'] = elm.attrs['content']

	# extracts the 'keywords' metatag
	elm = soup.find('meta', attrs = {'name': 'Keywords'})
	if (elm): ds['main']['keywords'] = [ tmp.strip() for tmp in elm.attrs['content'].split(',') ]

# extracts ingredients list
def ingredientsScraper(soup, ds):

	try:
		for elm in soup.find('div', {'class': 'ingredients'}).find('ul', {'id': 'ingredienti'}).findAll('li', {'class': 'hddn'}):
			ds['ingredients'].append(elm.text.strip())

	except:
		pass

def relatedRecipesScraper(soup, ds):
	# at the end of the presentation, in general, the url of a strongly correlated recipe is indicated; e.g.:
	# "Leggi anche: Zucca gratinata"
	# this code snippet extracts that text-url pair
	try:
		# extracts the first child element <p> (text presentation)
		elm = soup.select('div.gz-content-recipe > p')[1].find('a')
		if (elm): ds['related_recipes'][elm['href']] = elm.text
	except Exception as e:
		pass

	# within the presentation text there are some keywords (recipe names, in general) linked to related recipes
	# they are useful from a recipe map perspective
	try:
		elm = soup.select('div.gz-content-recipe > p')[0]
		for url in elm.findAll('a'):
			if (elm): ds['related_recipes'][url['href']] = url.text
	except Exception as e:
		pass

	# at the bottom of the page, in general, we can find the "related recipes" section
	try:
		for elm in soup.select('article.gz-card-related h2.gz-title a'):
			ds['related_recipes'][elm['href']] = elm.text
	except Exception as e:
		pass

# returns an empty data structure (based on dictionaries) useful as base skeleton to be easily transformed into a json 
# and, subsequently, into a MongoDB collection
def getDataStructurePrototype():
    dataStructure = {
    	'url': { },
        'main': { },
        'features': { },
        'ingredients': [ ],
    }
    return dataStructure

# in case we need a json file
# thread-safe method
def fileWriter(output):
	lock.acquire()
	try:
		with open(outputFile, 'a') as outfile:
			json.dump(output, outfile, indent = 2, ensure_ascii = False)
	finally:
	    lock.release() 

# let's start ;-)
if __name__ == '__main__':
    main()