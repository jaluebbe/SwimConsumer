import redis
import json
import logging
import time
import arrow
from flight_database import FlightDatabase

logging.basicConfig(level=logging.WARNING)
redis_connection = redis.Redis("redis", decode_responses=True)
flight_db = FlightDatabase()


def process_message(message):
    if message["airline"] in ("XXX", "DCM", "FWR", "FFL", "XAA"):
        return

    # Split callsign into operator and suffix and remove leading zeros.
    operator_icao = message["callsign"][:3]
    suffix = message["callsign"][3:].lstrip("0")
    callsign = "{}{}".format(operator_icao, suffix)
    if not message["etd"]["etdType"] == "ACTUAL":
        return
    departure = int(arrow.get(message["etd"]["timeValue"]).timestamp())
    arrival = int(arrow.get(message["eta"]["timeValue"]).timestamp())
    duration = arrival - departure
    if duration <= 0:
        logging.warning(f"departure >= arrival: {message}")
        return
    if message["igtd"] is not None:
        igtd = int(arrow.get(message["igtd"]).timestamp())
    else:
        igtd = None
    if message.get("gate_departure") is not None:
        gate_departure = int(arrow.get(message["gate_departure"]).timestamp())
        if gate_departure > departure:
            logging.warning(f"gate_departure > departure: {message}")
            return
    else:
        gate_departure = None
    if message.get("gate_arrival") is not None:
        gate_arrival = int(arrow.get(message["gate_arrival"]).timestamp())
        if gate_arrival < arrival:
            logging.warning(f"gate_arrival < arrival: {message}")
            return
    else:
        gate_arrival = None
    origin = message["origin"]
    destination = message["destination"]
    historic_flight = {
        "callsign": callsign,
        "igtd": igtd,
        "gate_departure": gate_departure,
        "origin": origin,
        "departure": departure,
        "departure_actual": message["etd"]["etdType"] == "ACTUAL",
        "destination": destination,
        "arrival": arrival,
        "arrival_actual": message["eta"]["etaType"] == "ACTUAL",
        "gate_arrival": gate_arrival,
    }
    logging.debug(json.dumps(historic_flight, indent=2))
    logging.info(
        f"{callsign} {origin}-{destination} {duration / 60:.1f} minutes"
    )
    redis_connection.set("historic_flight_processed", time.time())
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
