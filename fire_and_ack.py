import json
import pandas as pd

import requests

from tqdm import tqdm
import threading

val_df = pd.read_csv("./model_train/Data/fashion-mnist_test.csv")
url = "http://localhost:5005/items"


def fire_kafka():
    # for i in tqdm(range(0, len(val_df)//2)):
    for i in tqdm(range(0, 5000)):
    
        payload = json.dumps({
          "image": val_df.iloc[i,1:].tolist(),
          "broker":"kafka"
        })
        headers = {
          'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)


def fire_rmq():
    # for i in tqdm(range(len(val_df)//2, len(val_df))):
    for i in tqdm(range(5000, 10000)):
    
        payload = json.dumps({
          "image": val_df.iloc[i,1:].tolist(),
          "broker":"pubsub"
        })
        headers = {
          'Content-Type': 'application/json'
        }
        
        response = requests.request("POST", url, headers=headers, data=payload)
        
        print(response.text)


kafka_thread = threading.Thread(target = fire_kafka, args = [])
rmq_thread = threading.Thread(target = fire_rmq, args = [])

kafka_thread.start()
rmq_thread.start()


    
    