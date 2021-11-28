#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 17 21:09:55 2021

@author: msabry
"""


import asyncio

from threading import Thread

import confluent_kafka
from confluent_kafka import KafkaException

import pika

#Kafka Producer class
class AIOProducer:
    def __init__(self, configs, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._producer = confluent_kafka.Producer(configs)
        self._cancelled = False
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def _poll_loop(self):
        while not self._cancelled:
            self._producer.poll(0.1)
    
    def close(self):
        self._cancelled = True
        self._poll_thread.join()

    def produce(self, topic, value):
        result = self._loop.create_future()
        def ack(err, msg):
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err))
            else:
                self._loop.call_soon_threadsafe(
                    result.set_result, msg)
        self._producer.produce(topic, value, on_delivery=ack)
        return result



#RabbitMQ Producer class
class PikaProducer:
    def __init__(self, publish_queue_name, publish_exchange_name):
        self.publish_queue_name = publish_queue_name
        self.publish_exchange_name = publish_exchange_name
        self._connect()


    def _connect(self):
        self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('admin', 'admin')))
        self.channel = self.connection.channel()
        self.publish_queue = self.channel.queue_declare(queue=self.publish_queue_name, durable=True)
        self.publish_exchange = self.channel.exchange_declare(self.publish_exchange_name)
        self.queue_binding = self.channel.queue_bind(exchange=self.publish_exchange_name, queue=self.publish_queue_name)


    def send_message(self, body):
        try:
            if self.channel.is_closed:
                self._connect()
        except pika.exceptions.ConnectionWrongStateError:
            self._connect()
            
        result = self.channel.basic_publish(
                                    exchange=self.publish_exchange_name,
                                    routing_key=self.publish_queue_name,
                                    body=body,
                                    properties=pika.BasicProperties(
                                        delivery_mode=2,  # make message persistent
                                    ))
        return result


    def close(self):
        self.connection.close()
