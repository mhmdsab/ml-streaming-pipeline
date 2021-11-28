#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 13:45:04 2021

@author: msabry
"""
import os
import uvicorn

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

from pydantic import BaseModel

from utils import load_model, preprocess, predict

# Configuration
BACKBONE = 'resnet18'

IMAGE_SIZE = 64

IMAGE_BASE_SIZE = 28


FASHION_DICT = {0:'T-shirt/top',
                1:'Trouser',
                2:'Pullover',
                3:'Dress',
                4:'Coat',
                5:'Sandal',
                6:'Shirt',
                7:'Sneaker',
                8:'Bag',
                9:'Ankle boot'}


model = load_model(BACKBONE, IMAGE_SIZE)

    
# initialization
app = FastAPI()

class Item(BaseModel):
    pixels: list

@app.get("/", response_class=PlainTextResponse)
async def hello():
    return "THIS IS A FASHION MNIST APPLICATION"


@app.post('/predict')
async def create_user(pixels: Item):
    response = {'success': False}
    if pixels.pixels:
        pixels_list = pixels.pixels
    
        img_requested = preprocess(pixels_list, IMAGE_BASE_SIZE, IMAGE_SIZE)
        results = predict(img_requested, model, FASHION_DICT)
    
        response['predictions'] = results
        response['success'] = True
    return response


# main
if __name__ == '__main__':
    uvicorn.run('fastapi_server:app', host='0.0.0.0', port=5000)




