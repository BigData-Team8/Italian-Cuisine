"""
giallozafferano.it scraping.
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
	'kafkaHost': 'bigdata2.server.retebalducci.it',
	'kafkaPort': '9092',
	'consumerTopicName': 'giallozafferano.it_crawling',
	'producerTopicName': 'giallozafferano.it_scraping',
	'groupId': 'GZ_scraping',
	'numWorkerThreads': 10
}

# in case we need a local json file
outputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/giallo_zafferano.json'

lock = threading.Lock()
threads = []

# in this database we have the information about the region of the recipe
r = redis.Redis(db = 0, port = 6310)



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
		if (url.startswith('[\'https://ricette.giallozafferano.it') and url.endswith('.html\']')):
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
			# produceContent(producer, ds)

			# writes to local file
			fileWriter(ds)

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

def scraper(ds, htmlContent):

	soup = BeautifulSoup(htmlContent, 'lxml')

	# scraping activities
	mainInfoScraper(soup, ds)
	metaTagScraper(soup, ds)
	ratingScraper(soup, ds)
	mainFeaturesScraper(soup, ds)
	otherFeaturesScraper(soup, ds)
	ingredientsScraper(soup, ds)
	nutritionInfoScraper(soup, ds)
	relatedRecipesScraper(soup, ds)

	# regionExtraction(ds)

	return ds

def mainInfoScraper(soup, ds):
	# title extraction:
	# option 1.
	# 	extracts the page title from <h1> tag
	# 	h1Title = soup.h1.getText()
	# 	ds['main']['title'] = h1Title
	# option 2.
	# 	extracts the page title from <title> tag
	# 	ds['main']['title_tag'] = soup.find('title').getText()
	# option 3.
	#	gets the title from metatag "og" 

	try:
		categories = []
		for elm in soup.find('div', {'class': 'gz-breadcrumb'}).find('ul').findAll('li'):
		# equivalent syntax:
		# for elm in soup.select('div.gz-breadcrumb')[0].find('ul').findAll('li'):
			for a in elm.findAll('a'):
				categories.append(a.text)

		if (categories): ds['main']['categories'] = categories
	except Exception as e:
		pass

	try:
		# extracts the text presentation of the recipe; it could be useful...
		elm = soup.select('div.gz-content-recipe > p')[0]
		if (elm): ds['main']['presentation'] = elm.text
	except Exception as e:
		pass

# this function can be used only after the Apache Nutch crawling of recipes' region
def regionExtraction(ds):
	region = r.get('GZ:url:' + ds['url'])
	if (region): ds['main']['region'] = region.decode('utf-8')
	return ds

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
	if (elm): ds['main']['url_meta'] = elm.attrs['content']

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
	if (elm):
		rating = elm['data-content-rate'] if (elm.has_attr('data-content-rate')) else 0

		# number of assessments (e.g.: '5 voti')
		elm = soup.find('div', {'class': 'rating_rate'})
		n = elm['title'].split(' ')[0] if (elm.has_attr('title')) else 0

		ds['main']['rating'] = [ rating, n ]

# extracts main features from the top-right box through BeautifulSoup
def mainFeaturesScraper(soup, ds):
	# luckily all the main features are contained by span elements with the same class
	for elm in soup.findAll('span', {'class': 'gz-name-featured-data'}):

		splitSep = ':'
		# special case in which the separator is '+' instead of ':'
		if elm.text.startswith('Nota'): splitSep = '+'

		elmText = elm.text.split(splitSep)

		# key-value pairs
		if len(elmText) == 2:
			# e.g.: from 'Dosi per' to 'dosi_per '; from 'Preparazione ' to 'preparazione'
			key = elmText[0].lower().strip().replace(' ', '_')
			# gets the entire text
			value = elmText[1].lower().strip()

		# finally, writes the result on the datastructure
		if (key): ds['features'][key] = value

# extracts other features from the top-right box through BeautifulSoup
def otherFeaturesScraper(soup, ds): 
	# luckily all the other features are contained by span elements with the same class
	otherFeatures = []
	for elm in soup.findAll('span', {'class': 'gz-name-featured-data-other'}):
		otherFeatures.append(elm.text)

	if (len(otherFeatures) > 0): ds['features']['other'] = otherFeatures

# extracts ingredients list
# honestly, it is not working as it should; for example, let's take a look to  https://ricette.giallozafferano.it/Whoopie.html
# the ingredient section is divided into 2 boxes; should we consider each box separately?
def ingredientsScraper(soup, ds):
	# luckily all the ingredients are contained by span elements with the same class
	for elm in soup.findAll('dd', {'class': 'gz-ingredient'}):
		key = elm.find('a').text.strip()
		value = ' '.join(elm.find('span').text.split())

		if (key): ds['ingredients'][key] = value

# scrapes all the nutrional values (Kcal and so on)
def nutritionInfoScraper(soup, ds):

	"""
	elm = soup.find('div', {'class': 'gz-text-calories-total'});
	if (elm):
		value = elm.find('span').text
		ds['nutrition']['kcal'] = value
	"""

	keys = []
	for elm in soup.findAll('span', {'class': 'gz-list-macros-name'}): keys.append(elm.text.strip())
	units = []
	for elm in soup.findAll('span', {'class': 'gz-list-macros-unit'}): units.append(elm.text)
	values = []
	for elm in soup.findAll('span', {'class': 'gz-list-macros-value'}): values.append(elm.text)

	# key-value pairs
	# ds['nutrition_info'] = dict(zip(keys, list(zip(units, values))))
    
    # json array [ "key, unit, value", "key, unit, value", .. ]
	nutritionInfo = []
	for key, unit, value in zip(keys, units, values): nutritionInfo.append(key + ', ' + unit + ', ' + value)
	ds['nutrition'] = nutritionInfo

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
        'related_recipes': { },
        'features': { },
        'nutrition': { },
        'ingredients': { },
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