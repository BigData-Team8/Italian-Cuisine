"""
The aim of this program is to merge the scraping data coming from Kafka and the recipe region coming from Redis
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
	'consumerTopicName': 'giallozafferano.it_scraping',
	'groupId': 'GZ_scraping_regions',
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

def worker():
	consumer = kafkaConsumer()

	regions = [ 'Abruzzo', 'Marche', 'Sardegna', 'Liguria', 'Friuli-Venezia-Giulia', 'Calabria',
				'Puglia', 'Umbria', 'Toscana', 'Valle-d-Aosta', 'Sicilia', 'Veneto', 'Piemonte',
				'Campania', 'Emilia-Romagna', 'Basilicata', 'Molise', 'Trentino-Alto-Adige', 'Lombardia' ]

	for msg in consumer:
		# gets the "payload" of the Kafka's message
		record = json.loads(msg.value)
		url = str(record['url'])
	
		print('working on: ' + url.strip('\n').strip())

		region = r.get('GZ:url:' + url)
		if (region):
			region = region.decode('utf-8')
			record['main']['region'] = [ region ]

		for region in regions:
			members = r.smembers('GZ:region:' + region)
			for value in members:

				value = value.decode('utf-8')

				# match!
				if (value == url):
					
					print('match in ' + region)

					try:
						if (region not in record['main']['region']):
							record['main']['region'].append(region)
					
					except:
						record['main']['region'] = [ region ]

		fileWriter(record)

	consumer.close()

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

# this function can be used only after the Apache Nutch crawling of recipes' region
def regionExtraction(url):
	return r.get('GZ:url:' + url)

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