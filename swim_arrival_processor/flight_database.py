import sqlite3
import logging

class FlightDatabase:
    logger = logging.getLogger(__name__)

    def __init__(self, db_file="swim_flight_history.sqb"):
        self.db_file = db_file
        self._connect()

    def _reconnect(self):
        self._disconnect()
        self._connect()

    def _disconnect(self):
        if self._connection is not None:
            self._connection.close()

    def _connect(self):
        try:
            self._connection = sqlite3.connect(self.db_file)
            self._connection.row_factory = sqlite3.Row
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
            if not retry:
                return self.submit_data(sql_query, params, retry=True)

    def set_historic_flight(self, historic_flight):
        if historic_flight["gate_departure"] is None:
            # SQLite does not support INSERT IGNORE directly, use a workaround
            sql_query = (
                "INSERT OR IGNORE INTO SWIMFlightHistory (Callsign, OriginIcao, IGTD, "
                "Departure, DepartureActual, DestinationIcao, Arrival, "
                "ArrivalActual, GateDeparture, GateArrival) VALUES (:callsign, "
                ":origin, :igtd, :departure, :departure_actual, "
                ":destination, :arrival, :arrival_actual, "
                ":gate_departure, :gate_arrival)"
            )
        else:
            sql_query = (
                "REPLACE INTO SWIMFlightHistory (Callsign, OriginIcao, IGTD, "
                "Departure, DepartureActual, DestinationIcao, Arrival, "
                "ArrivalActual, GateDeparture, GateArrival) VALUES (:callsign, "
                ":origin, :igtd, :departure, :departure_actual, "
                ":destination, :arrival, :arrival_actual, "
                ":gate_departure, :gate_arrival)"
            )
        return self.submit_data(sql_query, params=historic_flight)
