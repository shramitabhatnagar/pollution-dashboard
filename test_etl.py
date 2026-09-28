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
# CONFIGURATION
# ============================================================

API_URL = "https://airquality.xkdr.org/v1/measurements"

STATION_ID = "site_1406"
PARAMETER = "PM2.5"

START_DATE = "2024-12-01"
END_DATE = "2024-12-02"


# ============================================================
# STATION INFORMATION
# Temporary values for site_1406
# ============================================================

STATE = "Andhra Pradesh"
CITY = "Amaravati"
STATION = "Secretariat, Amaravati - APPCB"

LATITUDE = 16.5150833
LONGITUDE = 80.5181667


# ============================================================
# STEP 1 — FETCH DATA FROM XKDR
# ============================================================

print()
print("======================================")
print("STEP 1 - FETCHING XKDR DATA")
print("======================================")

params = {
    "station": STATION_ID,
    "parameter": PARAMETER,
    "start": START_DATE,
    "end": END_DATE,
    "agg": "hourly",
    "format": "json"
}

headers = {
    "Authorization": f"Bearer {XKDR_API_KEY}"
}

try:

    response = requests.get(
        API_URL,
        headers=headers,
        params=params,
        timeout=60
    )

    print("HTTP STATUS:", response.status_code)

    response.raise_for_status()

    result = response.json()

except requests.exceptions.RequestException as e:

    print()
    print("======================================")
    print("XKDR API ERROR")
    print("======================================")
    print(e)

    sys.exit(1)


data = result.get("data", [])

print("Records received:", len(data))

if not data:

    print("ERROR: XKDR returned no records.")
    sys.exit(1)

print()
print("FIRST RECORD:")
print(data[0])

print()
print("LAST RECORD:")
print(data[-1])


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
    print("======================================")
    print("AZURE SQL CONNECTION ERROR")
    print("======================================")
    print(e)

    sys.exit(1)


# ============================================================
# VERIFY DATABASE
# ============================================================

try:

    cursor.execute(
        """
        SELECT
            DB_NAME(),
            @@SERVERNAME
        """
    )

    database_name, server_name = cursor.fetchone()

    print("Database:", database_name)
    print("Server:", server_name)

except pyodbc.Error as e:

    print("Could not verify database:")
    print(e)

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# CHECK CURRENT ROW COUNT
# ============================================================

try:

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM pollution_raw
        """
    )

    before_count = cursor.fetchone()[0]

    print("Rows currently in pollution_raw:", before_count)

except pyodbc.Error as e:

    print()
    print("ERROR READING pollution_raw:")
    print(e)

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# INSERT STATEMENT
#
# IMPORTANT:
# station_id is required by your Azure SQL table.
# ============================================================

insert_sql = """
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
"""


# ============================================================
# STEP 3 — INSERT DATA
# ============================================================

print()
print("======================================")
print("STEP 3 - INSERTING DATA")
print("======================================")


inserted = 0
errors = 0


for index, row in enumerate(data, start=1):

    # --------------------------------------------------------
    # XKDR fields
    # --------------------------------------------------------

    station_id = row.get("station_id")

    timestamp = row.get("period_start")

    pollutant = row.get("parameter_name")

    min_val = row.get("min")

    max_val = row.get("max")

    avg_val = row.get("mean")


    # --------------------------------------------------------
    # Validate required fields
    # --------------------------------------------------------

    if not station_id:

        print()
        print("ERROR: station_id is missing")
        print("Record:", row)

        errors += 1
        continue


    if not timestamp:

        print()
        print("ERROR: period_start is missing")
        print("Record:", row)

        errors += 1
        continue


    if not pollutant:

        print()
        print("ERROR: parameter_name is missing")
        print("Record:", row)

        errors += 1
        continue


    # --------------------------------------------------------
    # INSERT
    # --------------------------------------------------------

    try:

        cursor.execute(
            insert_sql,

            station_id,
            timestamp,

            STATE,
            CITY,
            STATION,

            LATITUDE,
            LONGITUDE,

            pollutant,

            min_val,
            max_val,
            avg_val
        )

        inserted += 1

        print(
            f"[{index}/{len(data)}] "
            f"Inserted | "
            f"{station_id} | "
            f"{timestamp} | "
            f"{pollutant} | "
            f"{avg_val}"
        )

    except pyodbc.IntegrityError as e:

        print()
        print("======================================")
        print("INTEGRITY ERROR")
        print("======================================")

        print("Record:")
        print(row)

        print()
        print("SQL ERROR:")
        print(e)

        print("--------------------------------------")

        conn.rollback()

        errors += 1

    except pyodbc.Error as e:

        print()
        print("======================================")
        print("SQL ERROR")
        print("======================================")

        print("Record:")
        print(row)

        print()
        print("ERROR:")
        print(e)

        print("--------------------------------------")

        conn.rollback()

        errors += 1


# ============================================================
# STEP 4 — COMMIT
# ============================================================

print()
print("======================================")
print("STEP 4 - COMMITTING DATA")
print("======================================")

try:

    conn.commit()

    print("Transaction committed successfully.")

except pyodbc.Error as e:

    print()
    print("COMMIT ERROR:")
    print(e)

    conn.rollback()

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# STEP 5 — VERIFY FINAL ROW COUNT
# ============================================================

print()
print("======================================")
print("STEP 5 - VERIFYING DATABASE")
print("======================================")

try:

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM pollution_raw
        """
    )

    after_count = cursor.fetchone()[0]

except pyodbc.Error as e:

    print("Could not get final row count:")
    print(e)

    cursor.close()
    conn.close()

    sys.exit(1)


# ============================================================
# SHOW INSERTED RECORDS
# ============================================================

try:

    cursor.execute(
        """
        SELECT TOP 10
            id,
            station_id,
            last_update,
            state,
            city,
            station,
            pollutant,
            min_val,
            max_val,
            avg_val,
            inserted_at
        FROM pollution_raw
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    print()
    print("LATEST DATABASE RECORDS")
    print("--------------------------------------")

    for db_row in rows:
        print(db_row)

except pyodbc.Error as e:

    print("Could not read inserted records:")
    print(e)


# ============================================================
# CLOSE DATABASE
# ============================================================

cursor.close()
conn.close()


# ============================================================
# FINAL RESULT
# ============================================================

print()
print("======================================")
print("XKDR → AZURE SQL ETL COMPLETE")
print("======================================")

print(f"XKDR records received : {len(data)}")
print(f"Records inserted      : {inserted}")
print(f"Errors                : {errors}")
print(f"Rows before           : {before_count}")
print(f"Rows after            : {after_count}")
print(f"Net rows added        : {after_count - before_count}")

print("======================================")