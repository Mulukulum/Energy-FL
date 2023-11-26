import datetime
import tensorflow as tf
from tensorflow import keras
from keras.callbacks import Callback

class TimeHistory(Callback):
    
    def on_train_begin(self, logs={}):
        self.start_times : list[str] = []
        self.end_times : list[str] = []

    def on_epoch_begin(self, batch, logs={}):
        self.epoch_time_start = datetime.datetime.now().strftime(r"%H:%M:%S.%f")[:-4]
        self.start_times.append(self.epoch_time_start)

    def on_epoch_end(self, batch, logs={}):
        self.epoch_time_end = datetime.datetime.now().strftime(r"%H:%M:%S.%f")[:-4]
        self.end_times.append(self.epoch_time_end)