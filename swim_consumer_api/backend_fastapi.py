import re
from fastapi import FastAPI, Query, HTTPException, Depends
import arrow
import sqlite3

app = FastAPI(openapi_prefix="", title="SwimConsumer API", description="")

SWIM_DB_FILE = "swim_flight_history.sqb"
callsign_validator = re.compile(
    "^([A-Z]{3})[0-9](([0-9]{0,3})|([0-9]{0,2})([A-Z])|([0-9]?)([A-Z]{2}))$"
)


def parse_datetime(value: str):
    try:
        return int(value)
    except ValueError:
        return int(arrow.get(value).timestamp())


@app.get("/api/swim_arrival_status")
def get_swim_consumer_status():
    sql_query = """
        SELECT strftime('%s', 'now') - MAX(Arrival) AS LastUpdate
        FROM SWIMFlightHistory;"""
    with sqlite3.connect(SWIM_DB_FILE) as db_connection:
        db_connection.row_factory = sqlite3.Row
        _cursor = db_connection.cursor()
        _cursor.execute(sql_query)
        result = _cursor.fetchone()
    if result is not None:
        result_dict = dict(result)
        if result_dict["LastUpdate"] < 300:
            result_dict["Status"] = "OK"
        return result_dict


@app.get("/api/swim_flight_history")
def get_swim_flight_history(
    begin: str = Query(
        ..., description="Start time in epoch or datetime format"
    ),
    end: str = Query(
        None,
        description=(
            "End time in epoch or datetime format "
            "(defaults to 1 hour after begin)"
        ),
    ),
    show_datetime: bool = Query(default=False),
):
    begin_epoch = parse_datetime(begin)
    if end is None:
        end_epoch = begin_epoch + 3600
    else:
        end_epoch = parse_datetime(end)
    if begin_epoch > end_epoch or end_epoch - begin_epoch > 3600 * 24 * 7:
        raise HTTPException(status_code=404, detail="invalid time range")

    if show_datetime:
        sql_query = f"""
            SELECT Callsign, OriginIcao AS Origin, 
            datetime(IGTD, 'unixepoch') AS IGTD,
            datetime(GateDeparture, 'unixepoch') AS GateDeparture,
            datetime(Departure, 'unixepoch') AS Departure, DepartureActual,
            DestinationIcao AS Destination, 
            datetime(Arrival, 'unixepoch') AS Arrival,
            ArrivalActual, datetime(GateArrival, 'unixepoch') AS GateArrival
            FROM SWIMFlightHistory
            WHERE Departure BETWEEN {begin_epoch} AND {end_epoch};"""
    else:
        sql_query = f"""
            SELECT Callsign, OriginIcao AS Origin, IGTD, GateDeparture,
            Departure, DepartureActual, DestinationIcao AS Destination,
            Arrival, ArrivalActual, GateArrival
            FROM SWIMFlightHistory
            WHERE Departure BETWEEN {begin_epoch} AND {end_epoch};"""
    with sqlite3.connect(SWIM_DB_FILE) as db_connection:
        db_connection.row_factory = sqlite3.Row
        _cursor = db_connection.cursor()
        _cursor.execute(sql_query)
        result = _cursor.fetchall()

    result_list = []
    for _row in result:
        _row_dict = dict(_row)
        _row_dict["DepartureActual"] = bool(_row_dict["DepartureActual"])
        _row_dict["ArrivalActual"] = bool(_row_dict["ArrivalActual"])
        result_list.append(_row_dict)
    return result_list


@app.get("/api/swim_flight_history_by_callsign")
def get_swim_flight_history_by_callsign(
    callsign: str = Query(
        ..., description="Callsign representing an airline flight"
    ),
    days_back: int = Query(
        14,
        description=(
            "Number of days to go back from the current date "
            "(defaults to 14 days)"
        ),
    ),
):
    if not callsign_validator.match(callsign):
        raise HTTPException(
            status_code=400, detail="Unsupported callsign format"
        )
    begin_epoch = int(arrow.utcnow().shift(days=-days_back).timestamp())

    sql_query = f"""
        SELECT Callsign, OriginIcao AS Origin, IGTD, GateDeparture,
        Departure, DepartureActual, DestinationIcao AS Destination,
        Arrival, ArrivalActual, GateArrival
        FROM SWIMFlightHistory
        WHERE Callsign = ? AND Departure > ?;"""
    with sqlite3.connect(SWIM_DB_FILE) as db_connection:
        db_connection.row_factory = sqlite3.Row
        _cursor = db_connection.cursor()
        _cursor.execute(sql_query, (callsign, begin_epoch))
        result = _cursor.fetchall()

    result_list = []
    for _row in result:
        _row_dict = dict(_row)
        _row_dict["DepartureActual"] = bool(_row_dict["DepartureActual"])
        _row_dict["ArrivalActual"] = bool(_row_dict["ArrivalActual"])
        result_list.append(_row_dict)
    return result_list
