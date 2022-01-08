#!/usr/bin/env python
# encoding: utf-8
import csv
import requests
import json
import re
from collections import Counter

CSV_URL = "https://ourairports.com/data/airports.csv"

icao_pattern = re.compile("^[A-Z]{4}$")

with requests.Session() as s:
    download = s.get(CSV_URL)
    download.encoding = "utf-8"
reader = csv.DictReader(download.text.splitlines(), delimiter=",")
airports = [
    row for row in reader if icao_pattern.match(row["gps_code"]) is not None
]

icao_count = Counter()
for row in airports:
    icao_count.update([row["gps_code"]])
icao_count.subtract(list(icao_count))
duplicate_icaos = set(+icao_count)

airport_iata_to_icao = {}
for row in airports:
    if not len(row["iata_code"]) == 3:
        continue
    if row["type"] == "closed":
        continue
    if row["gps_code"] in duplicate_icaos and row["ident"] != row["gps_code"]:
        print(
            f"ignoring duplicate entry {row['ident']} for "
            f"{row['gps_code']} / {row['iata_code']}."
        )
        continue
    airport_iata_to_icao[row["iata_code"]] = row["gps_code"]

local_code_to_icao = {}
for row in airports:
    if len(row["iata_code"]) == 3:
        continue
    if len(row["local_code"]) != 3:
        continue
    if row["iso_country"] != "US":
        continue
    if row["type"] == "closed":
        continue
    local_code_to_icao[row["local_code"]] = row["gps_code"]


file_name = "airport_iata_to_icao.json"
print(f"writing {len(airport_iata_to_icao)} airports to {file_name}.")
with open(file_name, "w") as f:
    json.dump(airport_iata_to_icao, f)

file_name = "local_code_to_icao.json"
print(f"writing {len(local_code_to_icao)} airports to {file_name}.")
with open(file_name, "w") as f:
    json.dump(local_code_to_icao, f)
