import streamlit as st
import plotly.express as px
import pandas as pd


def show_tab4(df_hist):

    st.subheader(
        "📈 Time Series Trends"
    )

    if df_hist.empty:
        st.info(
            "Historical pollution data is not available."
        )
        return

    df = df_hist.copy()

    # ---------------------------------------------------------
    # Prepare data
    # ---------------------------------------------------------

    df["last_update"] = pd.to_datetime(
        df["last_update"],
        errors="coerce"
    )

    df["avg_val"] = pd.to_numeric(
        df["avg_val"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "last_update",
            "avg_val"
        ]
    )

    if df.empty:
        st.warning(
            "No valid historical records found."
        )
        return

    # ---------------------------------------------------------
    # Pollutant
    # ---------------------------------------------------------

    pollutants = sorted(
        df["pollutant"].dropna().unique()
    )

    if not pollutants:
        st.warning(
            "No pollutants available."
        )
        return

    pollutant = st.selectbox(
        "Select Pollutant",
        pollutants,
        key="tab4_pollutant"
    )

    filtered = df[
        df["pollutant"] == pollutant
    ].copy()

    # ---------------------------------------------------------
    # Station filter
    # ---------------------------------------------------------

    stations = sorted(
        filtered["station"].dropna().unique()
    )

    selected_station = st.selectbox(
        "Station",
        ["All Stations"] + stations,
        key="tab4_station"
    )

    if selected_station != "All Stations":

        filtered = filtered[
            filtered["station"] == selected_station
        ]

    # ---------------------------------------------------------
    # Daily trend
    # ---------------------------------------------------------

    filtered["date"] = (
        filtered["last_update"]
        .dt.date
    )

    daily = (
        filtered
        .groupby("date", as_index=False)
        ["avg_val"]
        .mean()
    )

    if daily.empty:
        st.warning(
            "No trend data available."
        )
        return

    fig = px.line(
        daily,
        x="date",
        y="avg_val",
        markers=True,
        title=(
            f"{pollutant} Daily Average"
        ),
        template="plotly_dark"
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=(
            f"Average {pollutant}"
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Hourly trend
    # ---------------------------------------------------------

    filtered["hour"] = (
        filtered["last_update"]
        .dt.hour
    )

    hourly = (
        filtered
        .groupby("hour", as_index=False)
        ["avg_val"]
        .mean()
    )

    fig_hour = px.line(
        hourly,
        x="hour",
        y="avg_val",
        markers=True,
        title=(
            f"{pollutant} Average by Hour"
        ),
        template="plotly_dark"
    )

    fig_hour.update_layout(
        xaxis_title="Hour of Day",
        yaxis_title=(
            f"Average {pollutant}"
        )
    )

    st.plotly_chart(
        fig_hour,
        use_container_width=True
    )