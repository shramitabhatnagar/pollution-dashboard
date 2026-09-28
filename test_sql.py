import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("AZURE_SQL_CONNECTION_STRING")

if not connection_string:
    raise Exception(
        "AZURE_SQL_CONNECTION_STRING is missing from .env"
    )

print("Connecting to Azure SQL...")

try:
    conn = pyodbc.connect(
        connection_string,
        timeout=30
    )

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            DB_NAME() AS database_name,
            GETUTCDATE() AS utc_time
    """)

    row = cursor.fetchone()

    print()
    print("================================")
    print("AZURE SQL CONNECTION SUCCESSFUL")
    print("================================")
    print("Database:", row.database_name)
    print("UTC Time:", row.utc_time)

    cursor.close()
    conn.close()

except Exception as e:

    print()
    print("================================")
    print("AZURE SQL CONNECTION FAILED")
    print("================================")
    print(e)