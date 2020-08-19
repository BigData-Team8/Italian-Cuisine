"""
Thanks to:
	https://medium.com/@manivannan_data/how-to-train-ner-with-custom-training-data-using-spacy-188e0e508c6
"""

from __future__ import unicode_literals, print_function
import spacy
from spacy.util import minibatch, compounding

import os
import json
import sys

import pickle
import plac
import random

modelFile = 'ingredients_NER_model'
# set modelStrategy to 'old' if you want to add new items to the trained model
modelStrategy = 'new'
# modelStrategy = 'old'

def trainModel(iterations):

	labels = [ 'O', 'AMT', 'ING' ]

	with open ('cucchiaio_ingredients_training_set.spacy', 'rb') as f:
	# with open ('gz_ingredients_training+test_set.spacy', 'rb') as f:
		trainData = pickle.load(f)

	# load existing spacy model
	if (modelStrategy == 'old'):
		nlp = spacy.load(modelFile)
		print('Loaded model ' + modelFile)
	else:
		# create blank Language class
		nlp = spacy.blank('it')
		print('Created blank \'it\' model')

	# create the built-in pipeline components and add them to the pipeline
	# nlp.create_pipe works for built-ins that are registered with spaCy
	if 'ner' not in nlp.pipe_names:
		ner = nlp.create_pipe('ner')
		nlp.add_pipe(ner, last = True)
	else:
		ner = nlp.get_pipe('ner')

	# create the built-in pipeline components and add them to the pipeline
	# nlp.create_pipe works for built-ins that are registered with spaCy
	if 'ner' not in nlp.pipe_names:
		ner = nlp.create_pipe('ner')
		nlp.add_pipe(ner, last = True)
	   
	# add labels
	# for _, annotations in trainData:
	#	for ent in annotations.get('entities'):
	#		ner.add_label(ent[2])
	# manually add labels
	for label in labels:
		ner.add_label(str(label))

	# get names of other pipes to disable them during training
	other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

	# only train NER
	with nlp.disable_pipes(*other_pipes):

		if (modelStrategy == 'new'):
			optimizer = nlp.begin_training()
		else:
			optimizer = nlp.entity.create_optimizer()

		for itn in range(iterations):

			print('Starting iteration n. ' + str(itn))
			
			# At each iteration, the training data is shuffled.
			# This ensure the model doesn’t make any generalizations based on the order of examples. 
			random.shuffle(trainData)
			losses = {}



			batches = minibatch(trainData, size = compounding(4., 32., 1.001))
			for batch in batches:
				texts, annotations = zip(*batch)
				nlp.update(texts, annotations, sgd = optimizer, drop = 0.25, losses = losses)

			print('Losses', losses)

			"""
			for text, annotations in trainData:
				nlp.update(
					[text],  			# batch of texts
					[annotations],  	# batch of annotations
					drop = 0.25,  		# dropout: make it harder to memorise data
					sgd = optimizer,	# callable to update weights
					losses = losses)
			"""
	return nlp

def main():

	# let's iterate 20 times
	NLP_model = trainModel(20)

	# save the created model
	NLP_model.to_disk(modelFile)

	"""
	testText = input('enter the text to test: ')
	doc = prdnlp(testText)
	for ent in doc.ents:
		print(ent.text, ent.start_char, ent.end_char, ent.label_)
	"""

# let's start ;-)
if __name__ == '__main__':
	main()