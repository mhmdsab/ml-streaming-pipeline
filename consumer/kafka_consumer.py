#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 18 12:37:53 2021

@author: msabry
"""

from confluent_kafka import Consumer, KafkaException
import sys
import json
import logging
from pprint import pformat
import requests
import json
from sqlalchemy import create_engine

def stats_cb(stats_json_str):
    stats_json = json.loads(stats_json_str)
    print('\nKAFKA Stats: {}\n'.format(pformat(stats_json)))


def register_consumbion(fashion_id, fashion_type):
    db_engine = create_engine('postgresql://postgres:password@192.168.100.239:5432/fashion_db')
    
    with db_engine.connect() as connection:
        registeration = connection.execute(f'''INSERT INTO fashion (fashion_id, fashion_type)
                                           VALUES ({fashion_id}, '{fashion_type}')''')

if __name__ == '__main__':
    # Consumer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    conf = {'bootstrap.servers': "192.168.100.239:9092", 
            # 'auto.create.topics.enable':True,
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
    # Hint: try debug='fetch' to generate some log messages
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
                sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                                 (msg.topic(), msg.partition(), msg.offset(),
                                  str(msg.key())))
                
                url = "http://localhost:5000/predict"
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

