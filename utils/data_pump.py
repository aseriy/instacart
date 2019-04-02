import keras
import numpy as np
import pandas as pd
import json
import gc


#train_x_file = '../Downloads/backup/train_x.json'
#train_y_file = '../Downloads/backup/train_y.json'
train_x_file = 'train_x.json'
train_y_file = 'train_y.json'

class DataPump():

	def __init__(self):

		#read in data using pandas
		train_X = pd.read_json(train_x_file, orient="split")
		train_X = train_X.replace(np.nan, 0)
		for col in train_X.columns.values:
			train_X[col] = train_X[col].astype('int32')

		train_Y = pd.read_json(train_y_file, orient="split")
		train_Y = train_Y.replace(np.nan, 0)
		for col in train_Y.columns.values:
			train_Y[col] = train_Y[col].astype('int32')

		#print train_X.shape
		#print train_Y.shape

		# Take a test sample
		test_idx = train_X.index[:-200]
		#print "test_idx", test_idx
		test_X = train_X.drop(test_idx)
		test_Y = train_Y.drop(test_idx)
		train_idx = train_X.index[train_X.shape[0]-200:]
		#print "train_idx", train_idx
		train_X.drop(train_idx, inplace=True)
		train_Y.drop(train_idx, inplace=True)

		#check data has been read in properly
		#print train_X.shape
		#print train_Y.shape
		#print test_X.shape
		#print test_Y.shape

		self.train_x = train_X
		self.train_y = train_Y
		self.test_x = test_X
		self.test_y = test_Y
		self.input_width = self.train_x.shape[1]
		self.output_width = self.train_y.shape[1]
		self.train_steps = self.train_x.shape[0]
		self.test_steps = self.test_x.shape[0]


	def pump_train(self):
		while True:
			for i in range(self.train_x.shape[0]):
				x = self.train_x.iloc[i].values
				y = self.train_y.iloc[i].values
				yield (np.array([x]), np.array([y]))
			gc.collect()

	def pump_test(self):
		while True:
			for i in range(self.test_x.shape[0]):
				x = self.test_x.iloc[i].values
				y = self.test_y.iloc[i].values
				yield (np.array([x]), np.array([y]))
			gc.collect()
