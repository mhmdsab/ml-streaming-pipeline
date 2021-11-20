#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 23:33:39 2021

@author: ahmed
"""

import os
import cv2
import numpy as np

import tensorflow as tf
from tensorflow.keras.models import Model 

from classification_models.tfkeras import Classifiers


##Build the model
def load_model(BACKBONE, img_size):
    model, preprocess_input = Classifiers.get(BACKBONE)
    resnet = model((img_size, img_size, 1), weights=None, include_top = False)
    
    bottle_neck = resnet.output
    top_layer = tf.keras.layers.GlobalAveragePooling2D(name='pool_layer')(bottle_neck)
    top_layer_classifier = tf.keras.layers.Dense(10, 
                                            activation = 'softmax', 
                                            name='emotions_output')(top_layer)
    
    
    model_ = Model(resnet.input, top_layer_classifier)
    model_.load_weights('{}/fashion-app/ckpt/{}_FASHION_MNIST.h5'.format(os.getcwd(), BACKBONE))
    return model_


def preprocess(pixels_list, img_base_size, img_size):
    img = np.array(pixels_list).reshape(img_base_size, img_base_size)/255.
    img = cv2.resize(img, (img_size, img_size))
    img = img[:,:,np.newaxis].astype('float32')
    return img
    

def predict(img, model, FASHION_DICT):
    # pred = model.predict(img)
    pred = model(np.expand_dims(img, 0))
    pred = np.argmax(pred, axis=-1)
    return FASHION_DICT[pred[0]]



