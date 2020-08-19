import os
import json
from bson import json_util
import sys

from kafka import KafkaConsumer
from kafka import KafkaProducer

import threading



# some configuration parameters
params = {
	'kafkaHost': 'bigdata2.server.retebalducci.it',
	'kafkaPort': '9092',
	'producerTopicName': 'datasets',
	'groupId': 'datasets_merge',

	# here we drastically removed any kind of parallel computation
	'numWorkerThreads': 1
}

threads = []

# iterates over the folder processing every html file inside it
def main():

	for i in range(params['numWorkerThreads']):
	    t = threading.Thread(target = worker)
	    t.start()
	    threads.append(t)

# https://stackoverflow.com/questions/40896024/if-you-have-less-consumers-than-partitions-what-happens/40935236
# multithreading and Kafka
# each thread consumes 'rawhtml' and, through the scraper, produces well-structured json
def worker():
	producer = kafkaProducer()

	inputFileCucchiaio = '../dataset/Cucchiaio_final.json'
	inputFileGZ = '../dataset/GialloZafferano_final.json'
	inputFileRR = '../dataset/RicetteRegionali_final.json'

	with open(inputFileCucchiaio) as jsonFile: cucchiaio_nodes = json.load(jsonFile)
	with open(inputFileGZ) as jsonFile:	GZ_nodes = json.load(jsonFile)
	with open(inputFileRR) as jsonFile: RR_nodes = json.load(jsonFile)

	for node in cucchiaio_nodes:
		produceContent(producer, node)

	for node in GZ_nodes:
		produceContent(producer, node)		

	for node in RR_nodes:
		produceContent(producer, node)

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
	print('working on ', data['url'])

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