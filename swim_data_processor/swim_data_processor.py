import redis
import json
import logging
import os

logging.basicConfig(level=logging.WARNING)
redis_connection = redis.Redis("redis", decode_responses=True)
if os.path.isfile("callsign_filter.txt"):
    with open("callsign_filter.txt") as f:
        callsign_filter = set(f.read().split())
else:
    callsign_filter = set()


def process_fdps_message(flights, show_raw_data=False):
    print(f"##### FDPS message with {len(flights)} items received #####")
    if isinstance(flights, dict):
        logging.debug(f"putting single flight into a list: {flights}")
        flights = [flights]
    for _flight in flights:
        flight = _flight["flight"]
        callsign = flight["flightIdentification"]["aircraftIdentification"]
        if callsign in callsign_filter:
            logging.debug(f"filtering '{callsign}'.")
            continue
        if flight.get("departure") is None:
            origin = None
        else:
            origin = flight["departure"].get("departurePoint")
        if flight.get("arrival") is None:
            destination = None
        else:
            destination = flight["arrival"].get("arrivalPoint")
        print(f"### {callsign} {origin}-{destination} ###")
        if show_raw_data:
            print(json.dumps(flight, indent=2))


def process_tfms_message(flights, show_raw_data=False):
    print(f"##### TFMS message with {len(flights)} items received #####")
    if isinstance(flights, dict):
        logging.debug(f"putting single flight into a list: {flights}")
        flights = [flights]
    for flight in flights:
        callsign = flight["acid"]
        if callsign in callsign_filter:
            logging.debug(f"filtering '{callsign}'.")
            continue
        origin = flight.get("depArpt")
        destination = flight.get("arrArpt")
        print(f"### {callsign} {origin}-{destination} ###")
        if show_raw_data:
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
