#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 15:27:45 2021

@author: msabry
"""


import pika
import json
import requests
from sqlalchemy import create_engine


url = "http://localhost:5000/predict"

def register_consumbion(fashion_id, fashion_type):
    db_engine = create_engine('postgresql://postgres:password@localhost:5432/fashion_db')
    
    with db_engine.connect() as connection:
        registeration = connection.execute(f'''INSERT INTO fashion (fashion_id, fashion_type, broker_type)
                                           VALUES ({fashion_id}, '{fashion_type}', 'RabbitMQ')''')



def callback_on_message_received(ch, method, properties, body):
    # deserialize the json string into an object
    payload = json.dumps({
                            "pixels": json.loads(body.decode('utf-8'))
                            })
    response = requests.request("POST", url, data=payload)
    print(f"{response.json()['predictions']} predicted from PubSub")
    register_consumbion(method.delivery_tag, response.json()['predictions'])
    ch.basic_ack(delivery_tag=method.delivery_tag)



if __name__ == '__main__':
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost', credentials=pika.PlainCredentials('admin', 'admin')))
            channel = connection.channel()
    
            channel.queue_declare(queue='items', durable=True)
            channel.basic_consume(queue='items', on_message_callback=callback_on_message_received)
            print(' [*] Waiting for messages. To exit press CTRL+C')
            try:
                channel.start_consuming()
                
            except KeyboardInterrupt:
                channel.stop_consuming()
                connection.close()
                break
            
    
    	# Recover from server-initiated connection closure - handles manual RMQ restarts
        except pika.exceptions.ConnectionClosedByBroker:
            continue
        # Do not recover on channel errors
        except pika.exceptions.AMQPChannelError as err:
            print("Channel error: {}, stopping...".format(err))
            break
        # Recover on all other connection errors
        except pika.exceptions.AMQPConnectionError:
            print("Connection was closed, retrying...")
            continue




