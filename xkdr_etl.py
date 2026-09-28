import os
import sys
import time
import requests
import pyodbc

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

XKDR_API_KEY = os.getenv("XKDR_API_KEY")
SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")

if not XKDR_API_KEY:
    print("ERROR: XKDR_API_KEY missing")
    sys.exit(1)

if not SQL_CONNECTION_STRING:
    print("ERROR: AZURE_SQL_CONNECTION_STRING missing")
    sys.exit(1)


# ============================================================
# XKDR CONFIGURATION
# ============================================================

API_URL = "https://airquality.xkdr.org/v1/measurements"

PARAMETERS = [
    "PM2.5",
    "PM10",
    "NO2",
    "NO",
    "NOx",
    "SO2",
    "Ozone",
    "CO",
    "NH3",
    "Benzene",
    "Toluene",
    "Xylene"
]

# How many stations to process in one execution
BATCH_SIZE = 25

# API timeout
API_TIMEOUT = 60


# ============================================================
# API HEADERS
# ============================================================

HEADERS = {
    "Authorization": f"Bearer {XKDR_API_KEY}",
    "Accept": "application/json"
}


# ============================================================
# DATABASE CONNECTION
# ============================================================

print()
print("==============================================")
print("CONNECTING TO AZURE SQL")
print("==============================================")

try:

    conn = pyodbc.connect(
        SQL_CONNECTION_STRING,
        timeout=30
    )

    cursor = conn.cursor()

    print("Azure SQL connected successfully.")

except pyodbc.Error as e:

    print("Azure SQL connection failed:")
    print(e)

    sys.exit(1)


# ============================================================
# GET STATIONS
# ============================================================

print()
print("==============================================")
print("LOADING STATIONS")
print("==============================================")


try:

    cursor.execute(
        """
        SELECT
            station_id,
            station_name,
            state_name,
            city_name,
            latitude,
            longitude
        FROM station_master
        WHERE station_id IS NOT NULL
        ORDER BY station_id
        """
    )

    stations = cursor.fetchall()

except pyodbc.Error as e:

    print("Could not load station_master:")
    print(e)

    cursor.close()
    conn.close()

    sys.exit(1)


print("Stations found:", len(stations))


if not stations:

    print("ERROR: No stations found.")

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# BATCH STATIONS
# ============================================================

stations_to_process = stations[:BATCH_SIZE]

print("Stations this run:", len(stations_to_process))


# ============================================================
# COUNTERS
# ============================================================

api_success = 0
api_failed = 0

records_received = 0
records_inserted = 0
duplicates = 0
errors = 0


# ============================================================
# PROCESS STATIONS
# ============================================================

for station_number, station in enumerate(
    stations_to_process,
    start=1
):

    (
        station_id,
        station_name,
        state_name,
        city_name,
        latitude,
        longitude
    ) = station


    print()
    print("----------------------------------------------")
    print(
        f"STATION {station_number}/{len(stations_to_process)}"
    )
    print("----------------------------------------------")

    print("ID    :", station_id)
    print("Name  :", station_name)
    print("State :", state_name)
    print("City  :", city_name)


    # ========================================================
    # FETCH EACH PARAMETER
    # ========================================================

    for parameter in PARAMETERS:

        params = {
            "station": station_id,
            "parameter": parameter,

            # Latest available period
            "start": "2024-12-01",
            "end": "2024-12-02",

            "agg": "hourly",
            "format": "json"
        }


        # ====================================================
        # API CALL
        # ====================================================

        try:

            response = requests.get(
                API_URL,
                headers=HEADERS,
                params=params,
                timeout=API_TIMEOUT
            )

            if response.status_code != 200:

                print(
                    f"API FAILED | "
                    f"{station_id} | "
                    f"{parameter} | "
                    f"HTTP {response.status_code}"
                )

                api_failed += 1
                continue


            result = response.json()

            data = result.get("data", [])

            api_success += 1

            records_received += len(data)

            print(
                f"{parameter:<10} "
                f"→ {len(data)} records"
            )


        except requests.exceptions.RequestException as e:

            print(
                f"API ERROR | "
                f"{station_id} | "
                f"{parameter} | "
                f"{e}"
            )

            api_failed += 1
            continue


        # ====================================================
        # INSERT DATA
        # ====================================================

        for row in data:

            measurement_station_id = row.get(
                "station_id"
            )

            timestamp = row.get(
                "period_start"
            )

            pollutant = row.get(
                "parameter_name"
            )

            min_val = row.get(
                "min"
            )

            max_val = row.get(
                "max"
            )

            avg_val = row.get(
                "mean"
            )


            # ================================================
            # VALIDATION
            # ================================================

            if not measurement_station_id:
                errors += 1
                continue

            if not timestamp:
                errors += 1
                continue

            if not pollutant:
                errors += 1
                continue


            # ================================================
            # DUPLICATE CHECK
            # ================================================

            try:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM pollution_raw
                    WHERE
                        station_id = ?
                        AND last_update = ?
                        AND pollutant = ?
                    """,
                    measurement_station_id,
                    timestamp,
                    pollutant
                )

                exists = cursor.fetchone()[0]


            except pyodbc.Error as e:

                print(
                    "Duplicate check failed:",
                    e
                )

                errors += 1
                continue


            if exists:

                duplicates += 1
                continue


            # ================================================
            # INSERT
            # ================================================

            try:

                cursor.execute(
                    """
                    INSERT INTO pollution_raw
                    (
                        station_id,
                        last_update,
                        state,
                        city,
                        station,
                        latitude,
                        longitude,
                        pollutant,
                        min_val,
                        max_val,
                        avg_val
                    )
                    VALUES
                    (
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?,
                        ?
                    )
                    """,

                    measurement_station_id,
                    timestamp,

                    state_name,
                    city_name,
                    station_name,

                    latitude,
                    longitude,

                    pollutant,

                    min_val,
                    max_val,
                    avg_val
                )

                records_inserted += 1


            except pyodbc.IntegrityError:

                # Unique index caught a duplicate
                duplicates += 1


            except pyodbc.Error as e:

                print()
                print("INSERT ERROR")
                print(e)

                errors += 1


        # ====================================================
        # COMMIT AFTER EACH PARAMETER
        # ====================================================

        try:

            conn.commit()

        except pyodbc.Error as e:

            print("Commit failed:")
            print(e)

            conn.rollback()

            errors += 1


# ============================================================
# FINAL DATABASE COUNT
# ============================================================

try:

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM pollution_raw
        """
    )

    final_count = cursor.fetchone()[0]

except pyodbc.Error:

    final_count = "UNKNOWN"


# ============================================================
# CLOSE
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL REPORT
# ============================================================

print()
print()
print("================================================")
print("        XKDR → AZURE SQL ETL COMPLETE")
print("================================================")

print()
print("Stations available :", len(stations))
print("Stations processed :", len(stations_to_process))

print("----------------------------------------------")

print("API successful     :", api_success)
print("API failed         :", api_failed)

print("----------------------------------------------")

print("Records received   :", records_received)
print("Records inserted   :", records_inserted)
print("Duplicates skipped :", duplicates)
print("Errors             :", errors)

print("----------------------------------------------")

print("Total DB rows      :", final_count)

print("================================================")