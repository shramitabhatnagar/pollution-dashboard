import streamlit as st
import pandas as pd


def show_tab3(df):

    st.subheader("📊 Analytics & Top Polluted Stations")

    if df.empty:
        st.info("No pollution data available.")
        return

    data = df.copy()

    data["max_val"] = pd.to_numeric(
        data["max_val"],
        errors="coerce"
    )

    data["avg_val"] = pd.to_numeric(
        data["avg_val"],
        errors="coerce"
    )

    # ---------------------------------------------------------
    # KPIs
    # ---------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Stations",
            data["station"].nunique()
        )

    with col2:
        st.metric(
            "States",
            data["state"].nunique()
        )

    with col3:
        st.metric(
            "Pollutants",
            data["pollutant"].nunique()
        )

    with col4:
        st.metric(
            "Records",
            len(data)
        )

    # ---------------------------------------------------------
    # Top stations
    # ---------------------------------------------------------

    st.subheader(
        "Top 15 Stations by Maximum Pollution"
    )

    top = (
        data
        .groupby(
            ["station", "state", "region"],
            as_index=False
        )
        .agg(
            maximum=("max_val", "max"),
            average=("avg_val", "mean")
        )
        .sort_values(
            "maximum",
            ascending=False
        )
        .head(15)
    )

    st.dataframe(
        top,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Pollutant summary
    # ---------------------------------------------------------

    st.subheader(
        "Pollutant Summary"
    )

    pollutant_summary = (
        data
        .groupby("pollutant", as_index=False)
        .agg(
            average=("avg_val", "mean"),
            maximum=("max_val", "max"),
            minimum=("min_val", "min")
        )
        .sort_values(
            "maximum",
            ascending=False
        )
    )

    st.dataframe(
        pollutant_summary,
        use_container_width=True
    )

    # ---------------------------------------------------------
    # Raw data
    # ---------------------------------------------------------

    with st.expander(
        "View Raw Latest Data"
    ):
        st.dataframe(
            data,
            use_container_width=True
        )