# SwimConsumer

This project consumes SWIM messages using the jumpstart package. The messages are published into a Redis channel "SWIM" which can be consumed by other programming languages. This project includes a simple Python script which prints received data to the screen.

## Requirements
You should have Docker installed. 
Create a swim_consumer.conf based on swim_consumer_example.conf including the SWIM credentials of your subscription. It should work at least with the FDPS or TFMS service.

Finally start the services by calling: 
```
docker-compose up
```

You may observe that there is still an non-negligible "Expired Message Count" for your subscription in the SWIM portal. In that case, you may increase the number of swim-consumer instances using the following statement instead:
```
docker-compose up --scale swim-consumer=2
```

The services are stopped by calling:
```
docker-compose down
```

If you modify the Python container, you could rebuild it by calling:
```
docker-compose build swim-data-processor
```

## Optional
If you don't want to implement your own software to be run in a Docker container, you could modify the redis entry in the docker-compose.yml in the following way:
```
  redis:
    image: redis:alpine
    restart: always
    ports:
      - "127.0.0.1:6379:6379"
```
Now you could access the Redis instance from other software running on the same computer.

If you need to filter callsigns, you could provide a list of callsigns which should be ignored by further processing.
Just modify the entry in the docker-compose.yml in the following way:
```
  swim-data-processor:
    restart: always
    image: swim-data-processor
    build: ./swim_data_processor/
    volumes:
      - $PWD/my_callsign_filter.txt:/app/callsign_filter.txt:ro
    depends_on:
      - redis
```
The text file should contain one callsign per line.
