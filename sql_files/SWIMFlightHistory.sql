CREATE TABLE IF NOT EXISTS SWIMFlightHistory (
  Callsign TEXT NOT NULL,
  OriginIcao TEXT NOT NULL,
  IGTD INTEGER DEFAULT NULL,
  Departure INTEGER NOT NULL,
  DepartureActual INTEGER NOT NULL,
  DestinationIcao TEXT NOT NULL,
  Arrival INTEGER NOT NULL,
  ArrivalActual INTEGER NOT NULL,
  GateDeparture INTEGER DEFAULT NULL,
  GateArrival INTEGER DEFAULT NULL,
  PRIMARY KEY (Departure, Callsign)
);

CREATE INDEX idx_callsign ON SWIMFlightHistory (Callsign);
CREATE INDEX idx_departure ON SWIMFlightHistory (Departure);
CREATE INDEX idx_arrival ON SWIMFlightHistory (Arrival);
CREATE INDEX idx_callsign_departure ON SWIMFlightHistory (Callsign, Departure);
