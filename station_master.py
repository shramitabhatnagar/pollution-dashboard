import os
import sys
import requests
import pyodbc

from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

XKDR_API_KEY = os.getenv("XKDR_API_KEY")
SQL_CONNECTION_STRING = os.getenv("AZURE_SQL_CONNECTION_STRING")


if not XKDR_API_KEY:
    print("ERROR: XKDR_API_KEY is missing from .env")
    sys.exit(1)

if not SQL_CONNECTION_STRING:
    print("ERROR: AZURE_SQL_CONNECTION_STRING is missing from .env")
    sys.exit(1)


# ============================================================
# XKDR CONFIGURATION
# ============================================================

API_URL = "https://airquality.xkdr.org/v1/stations"

headers = {
    "Authorization": f"Bearer {XKDR_API_KEY}"
}


# ============================================================
# STEP 1 — FETCH STATIONS
# ============================================================

print()
print("======================================")
print("STEP 1 - FETCHING STATIONS FROM XKDR")
print("======================================")

try:

    response = requests.get(
        API_URL,
        headers=headers,
        timeout=60
    )

    print("HTTP STATUS:", response.status_code)

    response.raise_for_status()

    result = response.json()

except requests.exceptions.RequestException as e:

    print()
    print("XKDR API ERROR:")
    print(e)

    sys.exit(1)


data = result.get("data", [])

print("Stations received:", len(data))

if not data:

    print("ERROR: No stations returned by XKDR.")
    sys.exit(1)


print()
print("FIRST STATION:")
print(data[0])


# ============================================================
# STEP 2 — CONNECT TO AZURE SQL
# ============================================================

print()
print("======================================")
print("STEP 2 - CONNECTING TO AZURE SQL")
print("======================================")

try:

    conn = pyodbc.connect(
        SQL_CONNECTION_STRING,
        timeout=30
    )

    cursor = conn.cursor()

    print("Azure SQL connected successfully.")

except pyodbc.Error as e:

    print()
    print("AZURE SQL CONNECTION ERROR:")
    print(e)

    sys.exit(1)


# ============================================================
# STEP 3 — INSERT / UPDATE STATIONS
# ============================================================

print()
print("======================================")
print("STEP 3 - LOADING STATION MASTER")
print("======================================")


inserted = 0
updated = 0
errors = 0


for index, station in enumerate(data, start=1):

    station_id = station.get("station_id")
    station_name = station.get("station_name")
    state_name = station.get("state_name")
    city_name = station.get("city_name")
    source = station.get("source")

    latitude = station.get("latitude")
    longitude = station.get("longitude")

    first_seen = station.get("first_seen")
    last_seen = station.get("last_seen")


    # --------------------------------------------------------
    # Validate station ID
    # --------------------------------------------------------

    if not station_id:

        print()
        print("ERROR: station_id missing")
        print(station)

        errors += 1
        continue


    try:

        # ----------------------------------------------------
        # Check whether station already exists
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM station_master
            WHERE station_id = ?
            """,
            station_id
        )

        exists = cursor.fetchone()[0]


        # ----------------------------------------------------
        # UPDATE existing station
        # ----------------------------------------------------

        if exists:

            cursor.execute(
                """
                UPDATE station_master
                SET
                    station_name = ?,
                    state_name = ?,
                    city_name = ?,
                    source = ?,
                    latitude = ?,
                    longitude = ?,
                    first_seen = ?,
                    last_seen = ?,
                    updated_at = GETUTCDATE()
                WHERE station_id = ?
                """,

                station_name,
                state_name,
                city_name,
                source,
                latitude,
                longitude,
                first_seen,
                last_seen,
                station_id
            )

            updated += 1


        # ----------------------------------------------------
        # INSERT new station
        # ----------------------------------------------------

        else:

            cursor.execute(
                """
                INSERT INTO station_master
                (
                    station_id,
                    station_name,
                    state_name,
                    city_name,
                    source,
                    latitude,
                    longitude,
                    first_seen,
                    last_seen
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
                    ?
                )
                """,

                station_id,
                station_name,
                state_name,
                city_name,
                source,
                latitude,
                longitude,
                first_seen,
                last_seen
            )

            inserted += 1


        print(
            f"[{index}/{len(data)}] "
            f"{station_id} | "
            f"{station_name}"
        )


    except pyodbc.Error as e:

        print()
        print("SQL ERROR")
        print("--------------------------------------")
        print("Station:", station)
        print("Error:", e)
        print("--------------------------------------")

        conn.rollback()

        errors += 1


# ============================================================
# STEP 4 — COMMIT
# ============================================================

print()
print("======================================")
print("STEP 4 - COMMITTING")
print("======================================")

try:

    conn.commit()

    print("Transaction committed successfully.")

except pyodbc.Error as e:

    print("COMMIT ERROR:")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# STEP 5 — VERIFY
# ============================================================

print()
print("======================================")
print("STEP 5 - VERIFYING STATION MASTER")
print("======================================")

try:

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM station_master
        """
    )

    total_stations = cursor.fetchone()[0]

    print("Total stations in Azure SQL:", total_stations)


    cursor.execute(
        """
        SELECT TOP 10
            station_id,
            station_name,
            state_name,
            city_name,
            source,
            latitude,
            longitude
        FROM station_master
        ORDER BY station_id
        """
    )

    rows = cursor.fetchall()

    print()
    print("SAMPLE STATIONS")
    print("--------------------------------------")

    for row in rows:
        print(row)


except pyodbc.Error as e:

    print("Verification error:")
    print(e)


# ============================================================
# CLOSE
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("======================================")
print("STATION MASTER LOAD COMPLETE")
print("======================================")

print("Stations received :", len(data))
print("Stations inserted :", inserted)
print("Stations updated   :", updated)
print("Errors             :", errors)
print("Total in database  :", total_stations)

print("======================================")