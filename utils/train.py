#!/usr/bin/env python

from keras.models import Sequential
from keras.layers import Dense
from keras.callbacks import EarlyStopping
import numpy as np
import pandas as pd

#train_x_file = '../Downloads/backup/train_x.json'
#train_y_file = '../Downloads/backup/train_y.json'
train_x_file = 'train_x.json'
train_y_file = 'train_y.json'

#read in data using pandas
train_X = pd.read_json(train_x_file, orient="split")
train_X = train_X.replace(np.nan, 0)
for col in train_X.columns.values:
    train_X[col] = train_X[col].astype('int32')

train_Y = pd.read_json(train_y_file, orient="split")
train_Y = train_Y.drop(columns=["dept","aisle"]).replace(np.nan, 0)
for col in train_Y.columns.values:
    train_Y[col] = train_Y[col].astype('int32')

#check data has been read in properly
print train_X.head()
print train_Y.head()

#quit()

#create model
model = Sequential()

#get number of columns in training data
x_n_cols = train_X.shape[1]

#add model layers
model.add(Dense(200, activation='relu', input_shape=(x_n_cols,)))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(200, activation='relu'))
model.add(Dense(1))

#compile model using mse as a measure of model performance
model.compile(optimizer='adam', loss='mean_squared_error')

#set early stopping monitor so the model stops training when it won't improve anymore
early_stopping_monitor = EarlyStopping(patience=3)

#train model
model.fit(train_X, train_Y,
			validation_split=0.2, epochs=30,
			callbacks=[early_stopping_monitor])
