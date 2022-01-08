import redis
import json
import logging
import os
import time

logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.WARNING)
redis_connection = redis.Redis("redis", decode_responses=True)
if os.path.isfile("callsign_filter.txt"):
    with open("callsign_filter.txt") as f:
        callsign_filter = set(f.read().split())
else:
    callsign_filter = set()


def process_fdps_message(flights, show_raw_data=False):
    logging.info(f"### FDPS message with {len(flights)} items received ###")
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
        logging.info(f"{callsign} {origin}-{destination}")
        if show_raw_data:
            print(json.dumps(flight, indent=2))


def process_arrival_information(flight):
    _arrival_info = flight["fdm:arrivalInformation"]
    _time_data = _arrival_info["nxcm:ncsmFlightTimeData"]
    igtd = _arrival_info["nxcm:qualifiedAircraftId"].get("nxce:igtd")
    destination = flight.get("arrArpt")
    origin = flight.get("depArpt")
    if None in (origin, destination):
        logging.warning(f"origin or destination missing for: {flight}")
        return
    message = {
        "callsign": flight["acid"],
        "airline": flight["airline"],
        "igtd": igtd,
        "etd": _time_data["nxcm:etd"],
        "eta": _time_data["nxcm:eta"],
        "origin": origin,
        "destination": destination,
    }
    logging.info(message)
    redis_connection.publish("SWIM-ARRIVALS", json.dumps(message))


def process_tfms_message(flights, show_raw_data=True):
    logging.debug(f"### TFMS message with {len(flights)} items received ###")
    if isinstance(flights, dict):
        logging.debug(f"putting single flight into a list: {flights}")
        flights = [flights]
    for flight in flights:
        callsign = flight["acid"]
        if callsign in callsign_filter:
            logging.debug(f"filtering '{callsign}'.")
            continue
        msg_type = flight["msgType"]
        origin = flight.get("depArpt")
        destination = flight.get("arrArpt")
        logging.debug(f"{callsign} {origin}-{destination} ({msg_type})")
        if msg_type == "arrivalInformation":
            process_arrival_information(flight)
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
    except redis.exceptions.ConnectionError:
        logging.exception("reconnecting to Redis in 5s.")
        time.sleep(5)
