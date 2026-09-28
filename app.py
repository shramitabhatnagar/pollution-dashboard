import streamlit as st
import time

from components import (
    load_latest_data,
    load_historical_data,
    regions,
    show_tab1,
    show_tab2,
    show_tab3,
    show_tab4,
    show_tab5,
    show_tab6,
    show_tab7,
)


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="India Pollution Pulse",
    layout="wide",
    page_icon="🌫️",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        .stApp {
            background-color: #0a0a0a;
            color: #e0e0e0;
        }

        header {
            background-color: #0a0a0a !important;
        }

        h1, h2, h3 {
            color: #bb86fc !important;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
        }

        .stTabs [data-baseweb="tab"] {
            color: #e0e0e0;
        }

        .stTabs [aria-selected="true"] {
            color: #bb86fc !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <h1 style='text-align: left; color: #bb86fc;'>
        🌫️ India Pollution Pulse
    </h1>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD DATA
# ============================================================

try:
    df = load_latest_data()
    df_hist = load_historical_data()

except Exception as e:
    st.error("Unable to load pollution data.")
    st.exception(e)
    st.stop()


# ============================================================
# VALIDATE LATEST DATA
# ============================================================

if df is None:
    st.warning("No recent data found.")
    st.stop()

if df.empty:
    st.warning("No recent data found.")
    st.stop()


# ============================================================
# LAST UPDATE
# ============================================================

# Railway was crashing because last_update does not always exist.
# Therefore, check that the column exists before accessing it.

if "last_update" in df.columns:

    try:
        last_update = df["last_update"].max()

        st.caption(
            f"Last data fetched: **{last_update}**"
        )

    except Exception:
        st.caption("Latest pollution data")

else:

    st.caption("Latest pollution data")


# ============================================================
# ADD REGION COLUMN
# ============================================================

df = df.copy()


if "state" in df.columns:

    df["region"] = df["state"].apply(
        lambda x: next(
            (
                reg
                for reg, states in regions.items()
                if x in states
            ),
            "Other",
        )
    )

else:

    # Prevent the dashboard from crashing if state is unavailable
    df["region"] = "Other"


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(
    [
        "🗺️ All Pollutants Map",
        "🟥 AQI Map",
        "📊 Analytics",
        "📈 Time Trends",
        "🏙️ Regional Comparison",
        "⏰ Hourly Patterns",
        "🎯 AQI Overview & KPIs",
    ]
)


# ============================================================
# TAB 1
# ============================================================

with tab1:

    try:
        show_tab1(df, regions)

    except Exception as e:
        st.error("Unable to load All Pollutants Map.")
        st.exception(e)


# ============================================================
# TAB 2
# ============================================================

with tab2:

    try:
        show_tab2(df, regions)

    except Exception as e:
        st.error("Unable to load AQI Map.")
        st.exception(e)


# ============================================================
# TAB 3
# ============================================================

with tab3:

    try:
        show_tab3(df)

    except Exception as e:
        st.error("Unable to load Analytics.")
        st.exception(e)


# ============================================================
# TAB 4
# ============================================================

with tab4:

    try:
        show_tab4(df_hist)

    except Exception as e:
        st.error("Unable to load Time Trends.")
        st.exception(e)


# ============================================================
# TAB 5
# ============================================================

with tab5:

    try:
        show_tab5(df)

    except Exception as e:
        st.error("Unable to load Regional Comparison.")
        st.exception(e)


# ============================================================
# TAB 6
# ============================================================

with tab6:

    try:
        show_tab6(df_hist)

    except Exception as e:
        st.error("Unable to load Hourly Patterns.")
        st.exception(e)


# ============================================================
# TAB 7
# ============================================================

with tab7:

    try:
        show_tab7(df)

    except Exception as e:
        st.error("Unable to load AQI Overview & KPIs.")
        st.exception(e)


# ============================================================
# AUTO REFRESH
# ============================================================

# Refresh every 60 seconds.
# Streamlit reruns the complete application.

time.sleep(60)

st.rerun()