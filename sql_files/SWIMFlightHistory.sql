CREATE TABLE IF NOT EXISTS `SWIMFlightHistory` (
  `Callsign` varchar(8) COLLATE utf8mb4_unicode_ci NOT NULL,
  `OriginIcao` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `IGTD` int(11) DEFAULT NULL,
  `Departure` int(11) NOT NULL,
  `DepartureActual` tinyint(1) NOT NULL,
  `DestinationIcao` varchar(4) COLLATE utf8mb4_unicode_ci NOT NULL,
  `Arrival` int(11) NOT NULL,
  `ArrivalActual` tinyint(1) NOT NULL,
  `GateDeparture` int(11) DEFAULT NULL,
  `GateArrival` int(11) DEFAULT NULL,
  PRIMARY KEY (`Departure`,`Callsign`),
  KEY `idx_callsign` (`Callsign`),
  KEY `idx_departure` (`Departure`),
  KEY `idx_arrival` (`Arrival`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
