"""
cucchiaio.it scraping.
The aim of this program is to interact with Kafka and, at the same time, perform scraping activities;
it consumes raw data coming from Apache Nutch and produces semi-structured json encoded data with the most relevant information.
"""

import os
import json
import sys
from lxml import html
from bs4 import BeautifulSoup
from bson import json_util

from kafka import KafkaConsumer
from kafka import KafkaProducer

import threading

# some configuration parameters
params = {
	'kafkaHost': 'bigdata2.server',
	'kafkaPort': '9092',
	'consumerTopicName': 'cucchiaio.it_crawling',
	'producerTopicName': 'cucchiaio.it_scraping',
	'groupId': 'cucchiaio_scraping',
	'numWorkerThreads': 10
}

# in case we need a local json file
outputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/cucchiaio.json'

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

		# breakpoint
		url = str(record['url'])
		if (url.startswith('[\'https://www.cucchiaio.it/ricetta/')):
			print('working on: ' + url)

		    # gets an empty data structure prototype that will contain all the scraped content of the current page
			ds = getDataStructurePrototype()
			# set the main identification attribute
			ds['url'] = url.replace('[\'', '').replace('\']', '')

			# deals with escaping sequences
			htmlContent = escapingCleaning(record)

			# let's start with the scraping
			ds = scraper(ds, htmlContent)

			# pushes the scraping json result to a Kafka brokers cluster
			produceContent(producer, ds)

			# writes to local file
			fileWriter(ds)
			# printToScreen(ds)

		else:
			print('discarding: ' + url)

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
		consumer_timeout_ms = 30000)

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
		# print('Message published successfully')

	except Exception as ex:
		print('Exception in publishing message')
		print(str(ex))

# scraping orchestrator
def scraper(ds, content):
	# the first option uses BeautifulSoup
	soup = BeautifulSoup(content, 'lxml')

	# scraping activities
	mainInfoScraper(soup, ds)
	metaTagScraper(soup, ds)
	mainFeaturesScraper(soup, ds)
	ingredientsScraper(soup, ds)
	relatedRecipesScraper(soup, ds)

	return ds

def mainInfoScraper(soup, ds):
	# extracts the page title from <h1> tag
	# h1Title = soup.h1.getText()
	# ds['main']['title'] = h1Title

	# extracts the page title from <title> tag
	# ds['main']['title_tag'] = soup.find('title').getText()

	try:
		excludeList = [ 'home', 'ricette' ]
		categories = []
		for elm in soup.find('div', {'class': 'briciole'}).findAll('a'):
			if (elm.text.lower()) not in excludeList:
				categories.append(elm.text)

		if (categories): ds['main']['categories'] = categories
	except Exception as e:
		pass

	try:
		# extracts the text presentation of the recipe; it could be useful...
		elm = soup.select('div.ogdesc-single > p')[0]
		if (elm): ds['main']['presentation'] = elm.text.strip()
	except Exception as e:
		pass

	# each recipe is correlated to a set of tags
	tags = []
	try:
		for elm in soup.find('div', {'class': 'tag'}).findAll('a'):
			tags.append(elm.text.strip())

		if (tags): ds['main']['tags'] = tags

	except Exception as e:
		pass

# extracts all useful metatags
def metaTagScraper(soup, ds):
	# extracts the page title from meta property tag
	# e.g.: <meta property="og:url" content="https://ricette.giallozafferano.it/Insalata-di-fagiolini.html" />
	elm = soup.find('meta', property = 'og:title')
	# if (elm): ds['metatag']['og']['title'] = elm.attrs['content']
	if (elm): ds['main']['title'] = elm.attrs['content']

	# extracts the page urls from meta property tag
	# e.g.: <meta property="og:url" content="https://ricette.giallozafferano.it/Insalata-di-fagiolini.html" />
	elm = soup.find('meta', property = 'og:url')
	if (elm): ds['main']['url'] = elm.attrs['content']

	# extracts the 'description' metatag
	elm = soup.find('meta', attrs = {'name': 'description'})
	if (elm): ds['main']['description'] = elm.attrs['content']
	
	# extracts the 'image' metatag
	elm = soup.find('meta', property = 'og:image')
	if (elm): ds['main']['image'] = elm.attrs['content']

	# extracts the 'keywords' metatag
	elm = soup.find('meta', attrs = {'name': 'keywords'})
	if (elm): ds['main']['keywords'] = [ tmp.strip() for tmp in elm.attrs['content'].split(',') ]

def ratingScraper(soup, ds):
	# rating [0..5]
	elm = soup.find('div', {'id': 'rating_panel'})
	rating = elm['data-content-rate'] if (elm.has_attr('data-content-rate')) else 0

	# number of assessments (e.g.: '5 voti')
	elm = soup.find('div', {'class': 'rating_rate'})
	n = elm['title'].split(' ')[0] if (elm.has_attr('title')) else 0

	ds['main']['rating'] = [ rating, n ]

# extracts main features from the top-right box through BeautifulSoup
# it extracts, also, nutritional values
def mainFeaturesScraper(soup, ds):

	try:
		for elm in soup.find('div', {'class': 'scheda-ricetta-new'}).findAll('tr'):

			key = elm.select('td')[0].text.lower().capitalize()
			value = elm.select('td')[1].text.lower().capitalize()

			if (key == "Calorie"): ds['nutrition'][key] = value
			else: ds['features'][key] = value

	except Exception as e:
		pass

def ingredientsScraper(soup, ds):
	ingredients = []
	try:
		for elm in soup.select('div.lista-ingredienti-container')[0].select('ul.ingredients-list li'):

			# it skips upper-case text that, for sure, is not an ingredient
			if (elm.text.isupper()): continue
			ds['ingredients'].append(elm.text.strip())

		return ingredients
	except Exception as e:
		print(e)
		pass

def relatedRecipesScraper(soup, ds):
	# at the bottom of the page, in general, we can find the "related recipes" section
	# e.g.: SCOPRI ALTRE RICETTE SIMILI A "INVOLTINI DI MELANZANE E ZUCCHINE CON SPECK E MOZZARELLA"
	try:
		for elm in soup.select('div.related_contents div.fl_sx a'):

			if (elm['href'].startswith('/ricetta')):
				href = 'https://www.cucchiaio.it' + elm['href']
				# Unfortunately the text (value part of the pair) is truncated
				ds['related_recipes'][href] = elm.find('img')['title']
	except Exception as e:
		pass

# returns an empty data structure (based on dictionaries) useful as base skeleton to be easily transformed into a json 
# and, subsequently, into a MongoDB collection
def getDataStructurePrototype():
    dataStructure = {
        'main': { },
        'related_recipes': { },
        'features': { },
        'ingredients': [ ]
    }
    return dataStructure

# just a skeleton ... 
def printToScreen(ds):
	print(json.dumps(ds, indent = 2, ensure_ascii = False))

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
    # print('\nlet\'s take a look to ' + outputFile + '\n')