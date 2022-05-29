import docker
import redis
import time
from dateutil import parser
import logging


redis_connection = redis.Redis("redis", decode_responses=True)
client = docker.from_env()

interval = 60
old_tx_packets = {}


def check_tfms_received():
    now = time.time()
    tfms_received = redis_connection.get("tfms_received")
    if tfms_received is None:
        logging.warning(
            "no TFMS messages received or swim-data-processor offline."
        )
        return False
    else:
        age = now - float(tfms_received)
        if age > 600:
            logging.warning(
                f"TFMS data outdated ({age:.1f}s)->"
                "swim-data-processor or swim-consumer offline?"
            )
            return False
        else:
            logging.debug(
                f"swim-data-processor OK (last message {age:.1f}s ago)"
            )
            return True


def check_historic_flight_processed():
    now = time.time()
    historic_flight_processed = redis_connection.get(
        "historic_flight_processed"
    )
    if historic_flight_processed is None:
        logging.warning(
            "no arrivals received or swim-arrival-processor offline."
        )
        return False
    else:
        age = now - float(historic_flight_processed)
        if age > 800:
            logging.warning(
                f"arrival data outdated ({age:.1f}s)->"
                "swim-arrival-processor offline?"
            )
            return False
        else:
            logging.debug(
                f"swim-arrival-processor OK (last message {age:.1f}s ago)"
            )
            return True


while True:
    tfms_received_ok = check_tfms_received()
    _start = time.time()
    swim_consumers = [
        _c
        for _c in client.containers.list()
        if _c.labels.get("com.docker.compose.service") == "swim-consumer"
    ]
    for _container in swim_consumers:
        _startup = parser.parse(
            _container.attrs["State"]["StartedAt"]
        ).timestamp()
        _stats = _container.stats(stream=False)
        _tx_packets = _stats["networks"]["eth0"]["tx_packets"]
        _age = time.time() - _startup
        if old_tx_packets.get(_container.name) is not None:
            _new_tx_packets = _tx_packets - old_tx_packets[_container.name]
            logging.debug(
                f"{_container.name} {_container.status}, {_age:.0f}s up, "
                f"{_new_tx_packets} new tx_packets"
            )
            if _age > 120 and (
                _tx_packets == old_tx_packets[_container.name]
                or not tfms_received_ok
            ):
                logging.warning(
                    f"restarting {_container.name} after {_age:.0f}s "
                    f"({_start:.0f})."
                )
                redis_connection.rpush(
                    "docker_watchdog",
                    f"restarting {_container.name} after {_age:.0f}s "
                    f"({_start:.0f}).",
                )
                _container.restart()
        old_tx_packets[_container.name] = _tx_packets
    flight_processing_ok = check_historic_flight_processed()
    swim_arrival_processors = [
        _c
        for _c in client.containers.list()
        if _c.labels.get("com.docker.compose.service")
        == "swim-arrival-processor"
    ]
    for _container in swim_arrival_processors:
        _startup = parser.parse(
            _container.attrs["State"]["StartedAt"]
        ).timestamp()
        _age = time.time() - _startup
        if _age > 300 and not flight_processing_ok:
            logging.warning(
                f"restarting {_container.name} after {_age:.0f}s "
                f"({_start:.0f})."
            )
            redis_connection.rpush(
                "docker_watchdog",
                f"restarting {_container.name} after {_age:.0f}s "
                f"({_start:.0f}).",
            )
            _container.restart()

    _duration = time.time() - _start
    time.sleep(max(0, min(interval, interval - _duration)))
