import streamlit as st
import plotly.express as px
import pandas as pd


def show_tab6(df_hist):

    st.subheader(
        "⏰ Hourly & Daily Pollution Patterns"
    )

    if df_hist.empty:
        st.info(
            "Historical pollution data is not available."
        )
        return

    df = df_hist.copy()

    # ---------------------------------------------------------
    # Create datetime fields
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
            "No valid historical data available."
        )
        return

    # ---------------------------------------------------------
    # Create derived fields
    # ---------------------------------------------------------

    df["hour"] = (
        df["last_update"]
        .dt.hour
    )

    df["date"] = (
        df["last_update"]
        .dt.date
    )

    # ---------------------------------------------------------
    # Pollutant selection
    # ---------------------------------------------------------

    pollutants = sorted(
        df["pollutant"]
        .dropna()
        .unique()
    )

    if not pollutants:
        st.warning(
            "No pollutants available."
        )
        return

    pollutant = st.selectbox(
        "Select Pollutant",
        pollutants,
        key="tab6_pollutant"
    )

    filtered = df[
        df["pollutant"] == pollutant
    ].copy()

    if filtered.empty:
        st.warning(
            "No data available for this pollutant."
        )
        return

    # ---------------------------------------------------------
    # Hourly average
    # ---------------------------------------------------------

    hourly = (
        filtered
        .groupby("hour", as_index=False)
        ["avg_val"]
        .mean()
        .sort_values("hour")
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
        yaxis_title="Average Value"
    )

    st.plotly_chart(
        fig_hour,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Hourly heatmap
    # ---------------------------------------------------------

    heatmap = (
        filtered
        .groupby(
            ["date", "hour"],
            as_index=False
        )
        ["avg_val"]
        .mean()
    )

    if not heatmap.empty:

        fig_heat = px.density_heatmap(
            heatmap,
            x="hour",
            y="date",
            z="avg_val",
            title=(
                f"{pollutant} Hourly Heatmap"
            ),
            color_continuous_scale="Viridis",
            template="plotly_dark"
        )

        fig_heat.update_layout(
            xaxis_title="Hour of Day",
            yaxis_title="Date"
        )

        st.plotly_chart(
            fig_heat,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # Daily trend
    # ---------------------------------------------------------

    daily = (
        filtered
        .groupby(
            "date",
            as_index=False
        )
        ["avg_val"]
        .mean()
    )

    if not daily.empty:

        fig_daily = px.line(
            daily,
            x="date",
            y="avg_val",
            markers=True,
            title=(
                f"{pollutant} Daily Average"
            ),
            template="plotly_dark"
        )

        fig_daily.update_layout(
            xaxis_title="Date",
            yaxis_title="Average Value"
        )

        st.plotly_chart(
            fig_daily,
            use_container_width=True
        )