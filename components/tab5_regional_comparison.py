import streamlit as st
import plotly.express as px
import pandas as pd


def show_tab5(df):

    st.subheader(
        "🏙️ Regional & State Comparison"
    )

    if df.empty:
        st.info(
            "No pollution data available."
        )
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
    # Region comparison
    # ---------------------------------------------------------

    region_data = (
        data
        .groupby("region", as_index=False)
        .agg(
            average=("avg_val", "mean"),
            maximum=("max_val", "max")
        )
        .sort_values(
            "average",
            ascending=False
        )
    )

    # ---------------------------------------------------------
    # State comparison
    # ---------------------------------------------------------

    state_data = (
        data
        .groupby("state", as_index=False)
        .agg(
            average=("avg_val", "mean"),
            maximum=("max_val", "max")
        )
        .sort_values(
            "average",
            ascending=False
        )
        .head(10)
    )

    col1, col2 = st.columns(2)

    with col1:

        fig_region = px.bar(
            region_data,
            x="region",
            y="average",
            title="Average Pollution by Region",
            color="average",
            color_continuous_scale="Reds",
            template="plotly_dark"
        )

        fig_region.update_layout(
            xaxis_title="Region",
            yaxis_title="Average Pollution"
        )

        st.plotly_chart(
            fig_region,
            use_container_width=True
        )

    with col2:

        fig_state = px.bar(
            state_data,
            x="average",
            y="state",
            orientation="h",
            title="Top 10 States by Average Pollution",
            color="average",
            color_continuous_scale="Reds",
            template="plotly_dark"
        )

        fig_state.update_layout(
            xaxis_title="Average Pollution",
            yaxis_title="State"
        )

        st.plotly_chart(
            fig_state,
            use_container_width=True
        )

    # ---------------------------------------------------------
    # Detailed table
    # ---------------------------------------------------------

    st.subheader(
        "Regional Summary"
    )

    st.dataframe(
        region_data,
        use_container_width=True
    )