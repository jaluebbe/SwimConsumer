from fastapi import FastAPI, Query, HTTPException
import sqlite3

app = FastAPI(openapi_prefix="", title="SwimConsumer API", description="")

SWIM_DB_FILE = "swim_flight_history.sqb"


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
    begin: int, end: int, show_datetime: bool = Query(default=False)
):
    if begin > end or end - begin > 3600 * 24 * 7:
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
            WHERE Departure BETWEEN {begin} AND {end};"""
    else:
        sql_query = f"""
            SELECT Callsign, OriginIcao AS Origin, IGTD, GateDeparture,
            Departure, DepartureActual, DestinationIcao AS Destination,
            Arrival, ArrivalActual, GateArrival
            FROM SWIMFlightHistory
            WHERE Departure BETWEEN {begin} AND {end};"""
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
