import docker
import redis
import time
from dateutil import parser
import logging


redis_connection = redis.Redis("redis", decode_responses=True)
client = docker.from_env()

interval = 60
old_tx_packets = {}

while True:
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
            if _age > 120 and _tx_packets == old_tx_packets[_container.name]:
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
    _duration = time.time() - _start
    time.sleep(max(0, interval - _duration))
