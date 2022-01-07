# SwimConsumer

This project consumes SWIM messages using the jumpstart package. The messages are published into a Redis channel "SWIM" which can be consumed by other programming languages. This project includes a simple Python script which prints received data to the screen.

## Requirements
You should have Docker installed. 
Create a swim_consumer.conf based on swim_consumer_example.conf including the SWIM credentials of your subscription. It should work at least with the FDPS or TFMS service.

Finally start the services by calling: 
```
docker-compose up
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
