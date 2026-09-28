import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from .aqi_utils import calculate_station_aqi


def show_tab7(df):

    st.subheader(
        "🎯 AQI Overview & KPIs"
    )

    if df.empty:
        st.warning(
            "No data available for AQI calculation."
        )
        return

    data = df.copy()

    # ---------------------------------------------------------
    # Numeric cleanup
    # ---------------------------------------------------------

    for col in [
        "min_val",
        "max_val",
        "avg_val"
    ]:

        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    # ---------------------------------------------------------
    # Calculate AQI per station
    # ---------------------------------------------------------

    aqi_records = []

    for station in data["station"].dropna().unique():

        station_data = data[
            data["station"] == station
        ]

        try:

            aqi = calculate_station_aqi(
                station_data
            )

        except Exception:

            aqi = 0

        row = station_data.iloc[0]

        aqi_records.append(
            {
                "station": station,
                "state": row["state"],
                "city": row["city"],
                "aqi": aqi
            }
        )

    aqi_df = pd.DataFrame(
        aqi_records
    )

    if aqi_df.empty:
        st.warning(
            "Unable to calculate station AQI."
        )
        return

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------

    avg_aqi = round(
        aqi_df["aqi"].mean()
    )

    max_aqi = round(
        aqi_df["aqi"].max()
    )

    station_count = (
        aqi_df["station"].nunique()
    )

    severe_count = (
        aqi_df["aqi"] > 300
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Average AQI",
            avg_aqi
        )

    with col2:

        st.metric(
            "Highest AQI",
            max_aqi
        )

    with col3:

        st.metric(
            "Total Stations",
            station_count
        )

    with col4:

        st.metric(
            "Severe Stations",
            int(severe_count)
        )

    # ---------------------------------------------------------
    # Gauge
    # ---------------------------------------------------------

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=avg_aqi,
            title={
                "text": "Average Air Quality Index"
            },
            gauge={
                "axis": {
                    "range": [0, 500]
                },
                "steps": [
                    {
                        "range": [0, 50],
                        "color": "green"
                    },
                    {
                        "range": [51, 100],
                        "color": "lightgreen"
                    },
                    {
                        "range": [101, 200],
                        "color": "yellow"
                    },
                    {
                        "range": [201, 300],
                        "color": "orange"
                    },
                    {
                        "range": [301, 400],
                        "color": "red"
                    },
                    {
                        "range": [401, 500],
                        "color": "darkred"
                    }
                ]
            }
        )
    )

    fig.update_layout(
        template="plotly_dark",
        height=450
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Station AQI table
    # ---------------------------------------------------------

    st.subheader(
        "Station AQI Details"
    )

    st.dataframe(
        aqi_df.sort_values(
            "aqi",
            ascending=False
        ),
        use_container_width=True
    )