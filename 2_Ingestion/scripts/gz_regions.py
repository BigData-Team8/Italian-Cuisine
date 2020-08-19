"""
giallozafferano.it scraping of summary pages by region containing recipes

1. a Kafka consumer reads raw data coming from Apache Nutch crawling
2. urls/recipes for each region are extracted 
3. finally, pairs url-region are stored into a Redis db
"""

import os
import json
from bson import json_util
import sys
from lxml import html
from bs4 import BeautifulSoup

from kafka import KafkaConsumer
from kafka import KafkaProducer

import redis

import threading

# some configuration parameters
params = {
	'kafkaHost': 'bigdata1.server',
	'kafkaPort': '9092',
	'consumerTopicName': 'giallozafferano.it_crawling_regions',
	'groupId': 'GZ_regions',
	'numWorkerThreads': 10
}

# in case we need a local json file
outputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/giallo_zafferano_regions.json'

lock = threading.Lock()
threads = []

r = redis.Redis(db = 0, port = 6310)



def main():

	for i in range(params['numWorkerThreads']):
	    t = threading.Thread(target = worker)
	    t.start()
	    threads.append(t)

# https://stackoverflow.com/questions/40896024/if-you-have-less-consumers-than-partitions-what-happens/40935236
# multithreading and Kafka
# each thread consumes 'rawhtml' and, through the scraper, produces well-structured json
def worker():
	consumer = kafkaConsumer()

	for msg in consumer:
		# gets the "payload" of the Kafka's message
		record = json.loads(msg.value)

		split = str(record['url']).rsplit('/', 2)
		region = split[1]

		print('working on ' + str(record['url']) + ' ' + region)

		# deals with escaping sequences
		htmlContent = escapingCleaning(record)

		# let's start with the scraping
		urls = scraper(htmlContent)

		# lock.acquire()
		try:
			for url in urls:

				print(url)

				# interacts with redis in 2 different ways:
				# 1. simple key-value pairs
				r.set('GZ:url:' + url, region)
				# 2. Redis sets: unordered collections of strings
				r.sadd('GZ:region:' + region, url)
				# use 'SMEMBERS' to get the set's content
				# e.g.:SMEMBERS GZ:region:Toscana

				# writes to local file
				ds = { 
					'region': region,
					'url': url
				}

				# print(ds)
				fileWriter(ds)

		finally:
		    # lock.release()
		    pass

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
		consumer_timeout_ms = 5000)

    return consumer

def scraper(htmlContent):

	soup = BeautifulSoup(htmlContent, 'lxml')
	urls = []

	# scraping activities
	for elm in soup.findAll('h2', {'class': 'gz-title'}):
		urls.append(elm.find('a')['href'])

	return urls

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