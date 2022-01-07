import redis
import json
import logging


redis_connection = redis.Redis("redis", decode_responses=True)


def process_fdps_message(flights):
    print(f"### FDPS message with {len(flights)} items received ###")
    for _flight in flights:
        if isinstance(_flight, str):
            logging.debug(f"skipping '{_flight}'.")
            continue
        flight = _flight["flight"]
        callsign = flight["flightIdentification"]["aircraftIdentification"]
        print(f"############### {callsign} ###############")
        print(json.dumps(flight, indent=2))


def process_tfms_message(flights):
    print(f"### FDPS message with {len(flights)} items received ###")
    for flight in flights:
        callsign = flight["acid"]
        print(f"############### {callsign} ###############")
        print(json.dumps(flight, indent=2))


def process_message(message):
    if message.get("ns5:MessageCollection") is not None:
        process_fdps_message(message["ns5:MessageCollection"]["message"])
    elif message.get("ds:tfmDataService") is not None:
        process_tfms_message(
            message["ds:tfmDataService"]["fltdOutput"]["fdm:fltdMessage"]
        )
    else:
        print(json.dumps(message, indent=2))


while True:
    try:
        _pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
        _pubsub.subscribe("SWIM")
        for message in _pubsub.listen():
            if not message["type"] == "message":
                continue
            process_message(json.loads(message["data"]))
    except IOError:
        logging.warning("reconnecting to Redis")
    except Exception:
        logging.exception("error occured")
