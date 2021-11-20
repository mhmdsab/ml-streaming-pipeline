# ml-kafka-pipeline
Template for integrating Kafka messaging broker in a complete streaming pipeline which passes the stream through an inference model then stores the predictions in a database.


**The system comprises the following components**

  1- Message broker to manage the stream, with a producer and consumer on top of it.
  
  2- Model server which recieves the image and returns the prediction.
  
  3- Psotgresql data base to store stream output connected to pgadmin to manage the database server.
  
  
  **Notes**
  
  - The producer api is asynchronous to ensure the robustness of the system.
  
  - The data attached is minimal to keep the file structure, all records can be found 
    via https://www.kaggle.com/zalando-research/fashionmnist
    
  - model training folder contains the training script. upon training, log file is created with all the 
    training details registered. 
  
  **HOW TO SETUP**
  
  1- Clone the repo.
  
  2- Install the dependencies in the requirements.txt file.
  
  3- Run run.sh file, now you have producer api up and running on port 5005 and model server on 5000.
  
  4- Replace the demo test set in model_train/Data folder.
  
  5- In a separate console, run python fire_and_ack.py to start streaming.
  
  
  **TODO**
  
  - Reform the system to be completely deployable via docker-swarm and kubernetes, which improves the scalabiltity
    and the performance of the system.
  
  
