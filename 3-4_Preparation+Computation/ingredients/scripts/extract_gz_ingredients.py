"""
the aim of this program is to extract unique ingredients from a giallozafferano.it_scraping Kafka topic
and write them to a file
"""

import os
import json
from bson import json_util
import sys

from kafka import KafkaConsumer

import threading
from threading import RLock



# some configuration parameters
params = {
	'kafkaHost': 'bigdata2.server',
	'kafkaPort': '9092',
	'consumerTopicName': 'giallozafferano.it_scraping',
	'groupId': 'GZ_ingredients',
	'numWorkerThreads': 10
}

outputFile = serverInfoFile = os.path.dirname(os.path.realpath(__file__)) + '/gz_ingredients'

threads = []
ingredients = {}
lock = threading.Lock()



def main():

	for i in range(params['numWorkerThreads']):
	    t = threading.Thread(target = worker)
	    t.start()
	    threads.append(t)

	# waits for all of them to finish
	for thread in threads:
		thread.join()
		
	# writes the dictionary to file
	with open(outputFile, 'w') as file:
		# file.write(json.dumps(ingredients))
	    for key in ingredients:
        	print(key, file = file)

	print('\nDONE!')
	print('let\'s take a look to ' + outputFile)

# https://stackoverflow.com/questions/40896024/if-you-have-less-consumers-than-partitions-what-happens/40935236
# multithreading and Kafka
# each thread consumes a list of ingredients got from a kafka topic
def worker():
	consumer = kafkaConsumer()

	for msg in consumer:
		# gets the 'payload' of the Kafka's message
		record = json.loads(msg.value, encoding = 'utf-8')
		# print(record['url'])
		for ingredient in record['ingredients']:
			
			# immediatly skip an ingredient if its format is not clean
			if (not clean(ingredient)): continue

			# in a thread-safe manner, write an ingredient on the dictionary in case it hasn't already been seen
			lock.acquire()
			try:
				if ingredient not in ingredients:
					ingredients[ingredient] = 1
					print(ingredient)
			finally:
				lock.release()

	consumer.close()

# basic cleaning function (it could be implemented as needed)
def clean(string):
	if len(string) <= 2: return False
	return True

# kafka-python consumer instance
def kafkaConsumer():
    consumer = KafkaConsumer(params['consumerTopicName'],
		bootstrap_servers = params['kafkaHost'] + ':' + params['kafkaPort'],
		auto_offset_reset = 'earliest',
		enable_auto_commit = True,
		api_version = (0, 10),
		group_id = params['groupId'],
		consumer_timeout_ms = 10000)

    return consumer

# let's start ;-)
if __name__ == '__main__':
    main()