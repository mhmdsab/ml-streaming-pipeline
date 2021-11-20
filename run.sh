docker-compose down && docker-compose up -d

sleep 15

uvicorn producer_api:app --port 5005 --app-dir="$(pwd)/producer-app" &  
uvicorn model_server:app --port 5000 --app-dir="$(pwd)/fashion-app" & 
python consumer/kafka_consumer.py & 