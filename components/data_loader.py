# components/data_loader.py

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection_string():
    """
    Build Azure SQL connection using Railway environment variables.

    Required Railway variables:
        AZURE_SQL_SERVER
        AZURE_SQL_DATABASE
        AZURE_SQL_USERNAME
        AZURE_SQL_PASSWORD
    """

    server = os.getenv("AZURE_SQL_SERVER")
    database = os.getenv("AZURE_SQL_DATABASE")
    username = os.getenv("AZURE_SQL_USERNAME")
    password = os.getenv("AZURE_SQL_PASSWORD")

    if not all([server, database, username, password]):
        return None

    # Remove tcp: if user has copied the full Azure server string
    server = server.replace("tcp:", "").strip()

    # Remove port if already supplied
    if "," in server:
        server = server.split(",")[0]

    connection_url = URL.create(
        "mssql+pymssql",
        username=username,
        password=password,
        host=server,
        port=1433,
        database=database,
    )

    return connection_url


@st.cache_resource
def get_engine():

    connection_url = get_connection_string()

    if connection_url is None:
        return None

    try:
        engine = create_engine(
            connection_url,
            pool_pre_ping=True,
            pool_recycle=1800,
            pool_size=2,
            max_overflow=3,
            connect_args={
                "login_timeout": 30,
                "timeout": 60,
            },
        )

        # Test connection
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")

        return engine

    except Exception as e:

        st.error(
            f"Azure SQL connection failed: {str(e)}"
        )

        return None


# ============================================================
# LATEST DATA
# ============================================================

@st.cache_data(ttl=300)
def load_latest_data():

    engine = get_engine()

    if engine is None:

        st.error(
            "Azure SQL connection is not configured. "
            "Please check Railway Variables."
        )

        return pd.DataFrame()

    query = """
        SELECT
            station,
            latitude,
            longitude,
            pollutant,
            min_val,
            max_val,
            avg_val,
            last_update,
            state,
            city
        FROM vw_latest_pollution
        WHERE latitude IS NOT NULL
          AND longitude IS NOT NULL
    """

    try:

        df = pd.read_sql(query, engine)

        if df.empty:
            return pd.DataFrame()

        df["last_update"] = pd.to_datetime(
            df["last_update"],
            errors="coerce"
        )

        return df

    except Exception as e:

        st.error(
            f"Latest pollution data could not be loaded: {str(e)}"
        )

        return pd.DataFrame()


# ============================================================
# HISTORICAL DATA
# ============================================================

@st.cache_data(ttl=300)
def load_historical_data():

    engine = get_engine()

    if engine is None:
        return pd.DataFrame()

    query = """
        SELECT
            id,
            station_id,
            last_update,
            state,
            city,
            station,
            latitude,
            longitude,
            pollutant,
            unit,
            min_val,
            max_val,
            avg_val,
            source,
            inserted_at
        FROM pollution_raw
        ORDER BY last_update
    """

    try:

        df_hist = pd.read_sql(
            query,
            engine
        )

        if df_hist.empty:
            return pd.DataFrame()

        # Convert timestamp
        df_hist["last_update"] = pd.to_datetime(
            df_hist["last_update"],
            errors="coerce"
        )

        # Create date
        df_hist["date"] = (
            df_hist["last_update"].dt.date
        )

        # Create hour
        df_hist["hour"] = (
            df_hist["last_update"].dt.hour
        )

        return df_hist

    except Exception as e:

        st.warning(
            f"Historical data load failed: {str(e)}"
        )

        return pd.DataFrame()