from datetime import datetime
from time import time
import json
import logging
import keras
import tensorflow as tf
from keras import layers
from keras.models import Model
from keras.callbacks import EarlyStopping, TensorBoard, ModelCheckpoint
from keras import regularizers
import pickle
# from config.adaptive_lstm import Config
class AdaptiveGRU(keras.Model):
    def __init__(self, config):
        super(AdaptiveGRU, self).__init__()
        self.config = config
        self.timestep = self.config.timestep
        self.n_features = self.config.n_features
        self.n_classes  = self.config.n_classes 
        self.hidden_size = self.config.hidden_size
        self.kernel_size = self.config.kernel_size
        self.strides = self.config.strides
        self.filters = self.config.filters
        self.dropout = self.config.dropout 
        self.log_dir = self.config.log_dir
        self.save_file = self.config.save_file
        self.activation = self.config.activation
        self.regularizers = self.config.regularizers
        self.normalizer = self.config.normalizer
        self.lr  = self.config.lr
        self.optimizer = self.config.optimizer
        self.loss_fn = self.config.loss_fn
        self.normalizer = self.config.normalizer


        if self.config.regularizers == 'l1':
            self.regularizers = regularizers.L1(l1=0.1)
        elif self.config.regularizers == 'l2':
            self.regularizers = regularizers.L2(l2=0.1)
        elif self.config.regularizers == "l1_l2":
            self.regularizers = regularizers.L1L2(l1 = 0.1, l2=0.1)
        else:
            self.regularizers = None
    def build(self):
        input = keras.Input(shape=(self.timestep, self.n_features))
        x = input
        x = layers.Conv1D(filters=self.filters, kernel_size=self.kernel_size, strides=self.strides)(x)
        if self.normalizer == "batch_norm":
                x = layers.BatchNormalization()(x)
        elif self.normalizer == "layer_norm":
                x = layers.LayerNormalization(axis= -1, center=True , scale=True)(x)
        elif self.normalizer == "norm":
                x = tf.keras.layers.Normalization()(x)
        # elif self.normalizer == "instance_norm":
        #         x = tf.keras.layers.InstanceNormalization(axis=-1, 
        #                         center=True, 
        #                         scale=True,
        #                         beta_initializer="random_uniform",
        #                         gamma_initializer="random_uniform")(x)
        else:
                pass  
        for hidden in self.hidden_size:
            # x, h_state, c_state = layers.LSTM(units = hidden, activation = self.activation, return_sequences=True, kernel_regularizer=self.regularizers, return_state=True)(x)
            x, h_state = layers.GRU(units=hidden, activation=self.activation, return_sequences=True, kernel_regularizer=self.regularizers, return_state=True)(x)
            # if self.normalizer == "batch_norm":
            #     x = layers.BatchNormalization()(x)
            # elif self.normalizer == "layer_norm":
            #         x = layers.LayerNormalization(axis= -1, center=True , scale=True)(x)
            # elif self.normalizer == "norm":
            #         x = layers.Normalization()(x)
            # else:
            #     x = h_state
        x = h_state
        x = layers.Flatten()(x)
        x = layers.Dropout(self.dropout)(x)
        out = layers.Dense(self.n_classes, activation='softmax')(x)
        model = Model(inputs = input, outputs = out)

        return model 

