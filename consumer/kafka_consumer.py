#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:37:53 2021

@author: msabry
"""

import confluent_kafka
from confluent_kafka import Consumer, KafkaException
import sys
import json
import logging
import requests
from sqlalchemy import create_engine


url = "http://localhost:5000/predict"


def register_consumbion(fashion_id, fashion_type):
    db_engine = create_engine('postgresql://postgres:password@192.168.100.239:5432/fashion_db')
    
    with db_engine.connect() as connection:
        registeration = connection.execute(f'''INSERT INTO fashion (fashion_id, fashion_type, broker_type)
                                           VALUES ({fashion_id}, '{fashion_type}', 'kafka')''')

if __name__ == '__main__':
    # Consumer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    conf = {'bootstrap.servers': "192.168.100.239:9092", 
            'group.id': 'group1', 
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'}



    # Create logger for consumer (logs will be emitted when poll() is called)
    logger = logging.getLogger('consumer')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
    logger.addHandler(handler)

    # Create Consumer instance
    c = Consumer(conf, logger=logger)

    def print_assignment(consumer, partitions):
        print('Assignment:', partitions)

    # Subscribe to topics
    c.subscribe(["items"], on_assign=print_assignment)

    # Read messages from Kafka, print to stdout
    try:
        while True:
            msg = c.poll(timeout=1.0)
            if msg is None:
                continue
            if msg.error():
                raise KafkaException(msg.error())
            else:
                # Proper message
                sys.stderr.write('%% %s [%d] at offset %d: from kafka broker\n' %
                                 (msg.topic(), msg.partition(), msg.offset())
                                 )
                
                
                payload = json.dumps({
                                      "pixels": json.loads(msg.value().decode('utf-8'))
                                    })
                
                
                try:
                    response = requests.request("POST", url, data=payload)
                    print(response.json()['predictions'])
                except:
                    print("failed to call model server")

                try:
                    register_consumbion(msg.offset(), response.json()['predictions'])
                except Exception as e:
                    print(f"Failed to register message with offset {msg.offset()} to the database with error {e}")
                

    except KeyboardInterrupt:
        sys.stderr.write('%% Aborted by user\n')

    finally:
        # Close down consumer to commit final offsets.
        c.close()

