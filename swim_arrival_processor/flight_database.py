import mysql.connector
import json
import logging

with open("mysql_params.json") as f:
    mysql_params = json.load(f)


class FlightDatabase:
    logger = logging.getLogger(__name__)

    def __init__(self):
        self._connect()

    def _reconnect(self):
        self._disconnect()
        self._connect()

    def _disconnect(self):
        if self._connection is not None:
            self._connection.close()

    def _connect(self):
        try:
            self._connection = mysql.connector.connect(**mysql_params)
        except IOError:
            self.logger.exception("FlightDatabase._connect()")
            self._connection = None
            return False
        return True

    def submit_data(self, sql_query, params=None, retry=False):
        try:
            cursor = self._connection.cursor()
            cursor.execute(sql_query, params)
            cursor.close()
            self._connection.commit()
            return True
        except (IOError, Exception):
            self.logger.exception("FlightDatabase.submit_data()")
            self._reconnect()
            if retry == False:
                return self.submit_data(sql_query, params, retry=True)

    def set_historic_flight(self, historic_flight):
        sql_query = (
            "REPLACE INTO SWIMFlightHistory (Callsign, OriginIcao, IGTD, "
            "Departure, DepartureActual, DestinationIcao, Arrival, "
            "ArrivalActual) VALUES (%(callsign)s, %(origin)s, %(igtd)s, "
            "%(departure)s, %(departure_actual)s, %(destination)s, "
            "%(arrival)s, %(arrival_actual)s)"
        )
        return self.submit_data(sql_query, params=historic_flight)
