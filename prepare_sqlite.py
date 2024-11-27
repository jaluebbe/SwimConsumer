import pathlib
import sqlite3

PWD = pathlib.Path(__file__).resolve().parent
SWIM_FLIGHT_HISTORY_DB_FILE = PWD / "swim_flight_history.sqb"

with sqlite3.connect(SWIM_FLIGHT_HISTORY_DB_FILE) as db_connection:
    _cursor = db_connection.cursor()
    _cursor.execute(
        "SELECT count(name) FROM sqlite_master "
        "WHERE type='table' AND name='SWIMFlightHistory'"
    )
    if _cursor.fetchone()[0] == 0:
        with open(
            PWD / "sql_files/SWIMFlightHistory_sqlite.sql", encoding="utf-8"
        ) as f:
            db_connection.executescript(f.read())
    db_connection.commit()

with sqlite3.connect(SWIM_FLIGHT_HISTORY_DB_FILE) as db_connection:
    db_connection.execute("VACUUM")
