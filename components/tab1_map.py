import streamlit as st
import pydeck as pdk
import pandas as pd


def show_tab1(df, regions):

    st.subheader("🗺️ All Pollutants Map")

    if df.empty:
        st.info("No pollution data available.")
        return

    # ---------------------------------------------------------
    # Filters
    # ---------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        pollutants = sorted(
            df["pollutant"].dropna().unique().tolist()
        )

        selected_pollutants = st.multiselect(
            "Pollutants",
            pollutants,
            default=[],
            key="tab1_pollutants"
        )

    with col2:
        selected_regions = st.multiselect(
            "Regions",
            list(regions.keys()),
            default=[],
            key="tab1_regions"
        )

    with col3:
        states = sorted(
            df["state"].dropna().unique().tolist()
        )

        selected_states = st.multiselect(
            "States",
            states,
            default=[],
            key="tab1_states"
        )

    with col4:
        top_n = st.selectbox(
            "Top N Stations",
            [5, 10, 15, "All"],
            index=3,
            key="tab1_topn"
        )

    # ---------------------------------------------------------
    # Apply filters
    # ---------------------------------------------------------

    filtered = df.copy()

    if selected_pollutants:
        filtered = filtered[
            filtered["pollutant"].isin(selected_pollutants)
        ]

    if selected_regions:

        region_states = []

        for region in selected_regions:
            region_states.extend(regions[region])

        filtered = filtered[
            filtered["state"].isin(region_states)
        ]

    if selected_states:
        filtered = filtered[
            filtered["state"].isin(selected_states)
        ]

    # ---------------------------------------------------------
    # Top N
    # ---------------------------------------------------------

    if top_n != "All":

        top_stations = (
            filtered
            .groupby("station")["max_val"]
            .max()
            .nlargest(top_n)
            .index
        )

        filtered = filtered[
            filtered["station"].isin(top_stations)
        ]

    if filtered.empty:
        st.warning("No records match the selected filters.")
        return

    # ---------------------------------------------------------
    # Numeric conversion
    # ---------------------------------------------------------

    for col in [
        "latitude",
        "longitude",
        "min_val",
        "max_val",
        "avg_val"
    ]:
        filtered[col] = pd.to_numeric(
            filtered[col],
            errors="coerce"
        )

    filtered = filtered.dropna(
        subset=["latitude", "longitude"]
    )

    # ---------------------------------------------------------
    # Aggregate station data
    # ---------------------------------------------------------

    map_df = (
        filtered
        .groupby(
            ["station", "latitude", "longitude"],
            as_index=False
        )
        .agg(
            max_val=("max_val", "max"),
            min_val=("min_val", "min"),
            avg_val=("avg_val", "mean"),
            last_update=("last_update", "max"),
            state=("state", "first"),
            region=("region", "first")
        )
    )

    # ---------------------------------------------------------
    # Tooltip
    # ---------------------------------------------------------

    def create_tooltip(row):

        station_data = filtered[
            filtered["station"] == row["station"]
        ]

        lines = []

        for _, record in station_data.iterrows():

            lines.append(
                f"{record['pollutant']}: "
                f"Min {record['min_val']:.2f} | "
                f"Max {record['max_val']:.2f} | "
                f"Avg {record['avg_val']:.2f}"
            )

        return (
            f"<b>Station:</b> {row['station']}<br>"
            f"<b>State:</b> {row['state']}<br>"
            f"<b>Region:</b> {row['region']}<br>"
            f"<b>Last Update:</b> {row['last_update']}<br><br>"
            + "<br>".join(lines)
        )

    map_df["tooltip_details"] = map_df.apply(
        create_tooltip,
        axis=1
    )

    # ---------------------------------------------------------
    # Map
    # ---------------------------------------------------------

    view_state = pdk.ViewState(
        latitude=22.5,
        longitude=78.5,
        zoom=4.2,
        pitch=45
    )

    india_outline = pdk.Layer(
        "GeoJsonLayer",
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_telengana.geojson",
        stroked=True,
        filled=False,
        get_line_color=[100, 100, 100],
        line_width_min_pixels=1.5,
        opacity=0.8
    )

    column_layer = pdk.Layer(
        "ColumnLayer",
        map_df,
        get_position=["longitude", "latitude"],
        get_elevation="max_val",
        elevation_scale=800,
        radius=15000,
        get_fill_color=[255, 80, 60],
        pickable=True,
        auto_highlight=True
    )

    deck = pdk.Deck(
        layers=[
            india_outline,
            column_layer
        ],
        initial_view_state=view_state,
        map_style="mapbox://styles/mapbox/dark-v11",
        tooltip={
            "html": "{tooltip_details}",
            "style": {
                "background": "#1f2a44",
                "color": "white",
                "padding": "12px"
            }
        }
    )

    st.pydeck_chart(
        deck,
        use_container_width=True
    )