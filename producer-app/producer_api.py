#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 21:10:53 2021

@author: msabry
"""

import json
import uvicorn
from confluent_kafka import KafkaException
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from producers import AIOProducer, PikaProducer


app = FastAPI()

class Item(BaseModel):
    image: list
    broker: str

kafka_producer = None
PubSubProducer = None


@app.on_event("startup")
async def startup_event():
    global kafka_producer, PubSubProducer
    kafka_producer = AIOProducer( 
        {"bootstrap.servers": "localhost:9092"})
    
    PubSubProducer = PikaProducer("items", "items_exchange")


@app.on_event("shutdown")
def shutdown_event():
    kafka_producer.close()
    PubSubProducer.close()


@app.post("/items")
async def stream_item(item: Item):
    if item.broker == "kafka":
        try:
            result = await kafka_producer.produce("items", json.dumps(item.image).encode('utf-8'))
            return { "message": "Delivered for Kafka broker" }
        except KafkaException as ex:
            raise HTTPException(status_code=500, detail=ex.args[0].str())
    
    elif item.broker=="pubsub":
        result = PubSubProducer.send_message(json.dumps(item.image))
        return { "message": "Delivered for RabbitMQ broker" }
        
    else:
        return { "message": "Invalid Broker" }

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=5005)


