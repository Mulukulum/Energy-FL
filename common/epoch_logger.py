import datetime
import tensorflow as tf
from tensorflow import keras
from keras.callbacks import Callback

class TimeHistory(Callback):
    
    def on_train_begin(self, logs={}):
        self.start_times = []
        self.end_times = []

    def on_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = datetime.datetime.now()
        self.start_times.append(self.epoch_time_start)

    def on_epoch_end(self, batch, logs={}):
        self.epoch_time_end = datetime.datetime.now()
        self.end_times.append(self.epoch_time_end)