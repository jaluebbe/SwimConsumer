import redis
import json
import logging


redis_connection = redis.Redis('redis', decode_responses=True)


def process_message(message):
    flights = message['ns5:MessageCollection']['message']
    for _flight in flights:
        if isinstance(_flight, str):
            continue
        flight = _flight['flight']
        callsign = flight['flightIdentification']['aircraftIdentification']
        print(f"############### {callsign} ###############")
        print(json.dumps(flight, indent=2))


while True:
    try:
        _pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
        _pubsub.subscribe('SWIM')
        for message in _pubsub.listen():
            if not message['type'] == 'message':
                continue
            process_message(json.loads(message['data']))
    except IOError:
        logging.warning('reconnecting to Redis')
    except Exception:
        logging.exception('error occured')
