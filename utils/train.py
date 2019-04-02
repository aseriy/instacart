#!/usr/bin/env python

from keras.models import Sequential
from keras.layers import Dense
from keras.models import load_model


from data_pump import *

def generate_model(input_width, output_width):
	model = Sequential([
		Dense(input_width,
			input_shape=(input_width,),
			activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(input_width, activation='relu'),
		Dense(output_width, activation='relu'),
	])

	return model




def train(args):

	dp = DataPump()
#	samples = dp.pump_test()
#	print samples.next()

	model = generate_model(dp.input_width, dp.output_width)

	model.compile(loss='mean_squared_error',
				optimizer='adam',
				metrics=['accuracy'])

	model.fit_generator(dp.pump_train(),
						steps_per_epoch=dp.train_steps,
						epochs=20)

	result = model.evaluate_generator(
				dp.pump_test(), steps=dp.test_steps)
	print("Accuracy: %d" % round(result[1]*100))
	model.save('instacart_model.h5')


if __name__ == '__main__':

	import argparse
	parser = argparse.ArgumentParser()
	#parser.add_argument('--database', type=str, default="hosted")
	args = parser.parse_args()

	train(args)
