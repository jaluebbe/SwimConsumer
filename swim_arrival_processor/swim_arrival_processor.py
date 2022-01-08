import redis
import json
import logging
import time
import arrow
from flight_database import FlightDatabase

logging.basicConfig(level=logging.INFO)
redis_connection = redis.Redis("redis", decode_responses=True)
flight_db = FlightDatabase()


def process_message(message):
    if message["airline"] == "XXX":
        return

    # Split callsign into operator and suffix and remove leading zeros.
    operator_icao = message["callsign"][:3]
    suffix = message["callsign"][3:].lstrip("0")
    callsign = "{}{}".format(operator_icao, suffix)

    if message["igtd"] is not None:
        igtd = int(arrow.get(message["igtd"]).timestamp())
    else:
        igtd = None
    departure = int(arrow.get(message["etd"]["timeValue"]).timestamp())
    arrival = int(arrow.get(message["eta"]["timeValue"]).timestamp())
    origin = message["origin"]
    destination = message["destination"]
    historic_flight = {
        "callsign": callsign,
        "igtd": igtd,
        "origin": origin,
        "departure": departure,
        "departure_actual": message["etd"]["etdType"] == "ACTUAL",
        "destination": destination,
        "arrival": arrival,
        "arrival_actual": message["eta"]["etaType"] == "ACTUAL",
    }
    logging.debug(json.dumps(historic_flight, indent=2))
    duration = (arrival - departure) / 60
    logging.info(f"{callsign} {origin}-{destination} {duration:.1f} minutes")
    flight_db.set_historic_flight(historic_flight)


while True:
    try:
        _pubsub = redis_connection.pubsub(ignore_subscribe_messages=True)
        _pubsub.subscribe("SWIM-ARRIVALS")
        for message in _pubsub.listen():
            if not message["type"] == "message":
                continue
            process_message(json.loads(message["data"]))
    except redis.exceptions.ConnectionError:
        logging.exception("reconnecting to Redis in 5s.")
        time.sleep(5)
