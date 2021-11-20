import json
import pandas as pd

import requests

from tqdm import tqdm

val_df = pd.read_csv("./model_train/Data/fashion-mnist_test.csv")
url = "http://localhost:5005/items"

for i in tqdm(range(len(val_df))):

    payload = json.dumps({
      "name": val_df.iloc[i,1:].tolist()
    })
    headers = {
      'Content-Type': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)
    
    print(response.text)
