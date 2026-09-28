import streamlit as st
import pydeck as pdk
import pandas as pd

from .aqi_utils import (
    get_aqi_color,
    calculate_station_aqi
)


def show_tab2(df, regions):

    st.subheader("🟥 AQI Map")

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
            key="tab2_pollutants"
        )

    with col2:

        selected_regions = st.multiselect(
            "Regions",
            list(regions.keys()),
            default=[],
            key="tab2_regions"
        )

    with col3:

        states = sorted(
            df["state"].dropna().unique().tolist()
        )

        selected_states = st.multiselect(
            "States",
            states,
            default=[],
            key="tab2_states"
        )

    with col4:

        top_n = st.selectbox(
            "Top N Stations",
            [5, 10, 15, "All"],
            index=3,
            key="tab2_topn"
        )

    # ---------------------------------------------------------
    # Filter
    # ---------------------------------------------------------

    filtered = df.copy()

    if selected_pollutants:

        filtered = filtered[
            filtered["pollutant"].isin(
                selected_pollutants
            )
        ]

    if selected_regions:

        region_states = []

        for region in selected_regions:
            region_states.extend(
                regions[region]
            )

        filtered = filtered[
            filtered["state"].isin(region_states)
        ]

    if selected_states:

        filtered = filtered[
            filtered["state"].isin(selected_states)
        ]

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
    # AQI
    # ---------------------------------------------------------

    aqi_data = []

    for station in filtered["station"].dropna().unique():

        station_data = filtered[
            filtered["station"] == station
        ]

        try:
            aqi = calculate_station_aqi(
                station_data
            )
        except Exception:
            aqi = 0

        row = station_data.iloc[0]

        aqi_data.append(
            {
                "station": station,
                "latitude": row["latitude"],
                "longitude": row["longitude"],
                "state": row["state"],
                "region": row["region"],
                "aqi": aqi,
                "color": get_aqi_color(aqi)
            }
        )

    map_df = pd.DataFrame(aqi_data)

    if map_df.empty:
        st.warning("AQI could not be calculated.")
        return

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
        get_elevation="aqi",
        elevation_scale=60,
        radius=16000,
        get_fill_color="color",
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
            "html":
                "<b>Station:</b> {station}<br>"
                "<b>AQI:</b> {aqi}<br>"
                "<b>State:</b> {state}<br>"
                "<b>Region:</b> {region}",
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