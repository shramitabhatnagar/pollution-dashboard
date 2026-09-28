# app.py
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
    show_tab7
)

st.set_page_config(
    page_title="India Pollution Pulse",
    layout="wide",
    page_icon="🌫️"
)

# ============================================================
# GLOBAL DARK THEME
# ============================================================

st.markdown("""
<style>

.stApp {
    background-color: #0B1120 !important;
    color: #F8FAFC !important;
}

header {
    background-color: #0B1120 !important;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

h1, h2, h3, h4, h5, h6 {
    color: #FFFFFF !important;
}

p {
    color: #E2E8F0 !important;
}

[data-testid="stMarkdownContainer"] {
    color: #E2E8F0 !important;
}

[data-testid="stCaptionContainer"] {
    color: #CBD5E1 !important;
}

/* Buttons */
.stButton > button {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

.stButton > button:hover {
    background-color: #334155 !important;
    color: #FFFFFF !important;
    border-color: #60A5FA !important;
}

/* Selectboxes */
div[data-baseweb="select"] > div {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
    border: 1px solid #475569 !important;
}

div[data-baseweb="select"] span {
    color: #FFFFFF !important;
}

div[data-baseweb="select"] input {
    color: #FFFFFF !important;
}

div[role="listbox"] {
    background-color: #1E293B !important;
}

div[role="option"] {
    background-color: #1E293B !important;
    color: #FFFFFF !important;
}

div[role="option"]:hover {
    background-color: #334155 !important;
}

/* Multiselect */
[data-baseweb="tag"] {
    background-color: #334155 !important;
}

[data-baseweb="tag"] span {
    color: #FFFFFF !important;
}

/* Tabs */
button[data-baseweb="tab"] {
    color: #CBD5E1 !important;
    background-color: transparent !important;
    font-weight: 600 !important;
}

button[data-baseweb="tab"]:hover {
    color: #FFFFFF !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

div[data-baseweb="tab-highlight"] {
    background-color: #BB86FC !important;
}

/* Metrics */
div[data-testid="stMetric"] {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
    padding: 15px !important;
}

div[data-testid="stMetricLabel"] {
    color: #CBD5E1 !important;
}

div[data-testid="stMetricValue"] {
    color: #FFFFFF !important;
}

/* Expanders */
div[data-testid="stExpander"] {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px !important;
}

div[data-testid="stExpander"] summary {
    color: #FFFFFF !important;
}

/* Alerts */
div[data-testid="stAlert"] p {
    color: #FFFFFF !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0F172A !important;
}

section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: #FFFFFF !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid #374151 !important;
    border-radius: 8px !important;
}

/* Inputs */
input {
    color: #FFFFFF !important;
}

div[data-baseweb="input"] {
    background-color: #1E293B !important;
}

div[data-baseweb="input"] input {
    color: #FFFFFF !important;
}

/* Dividers */
hr {
    border-color: #334155 !important;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    "<h1 style='text-align: left; color: #BB86FC;'>🌫️ India Pollution Pulse</h1>",
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

df = load_latest_data()
df_hist = load_historical_data()

if df.empty:
    st.warning("No recent data found.")
    st.stop()

st.caption(f"Last data fetched: **{df['last_update'].max()}**")


# ============================================================
# ADD REGION
# ============================================================

df = df.copy()

df['region'] = df['state'].apply(
    lambda x: next(
        (reg for reg, states in regions.items() if x in states),
        "Other"
    )
)


# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗺️ All Pollutants Map",
    "🟥 AQI Map",
    "📊 Analytics",
    "📈 Time Trends",
    "🏙️ Regional Comparison",
    "⏰ Hourly Patterns",
    "🎯 AQI Overview & KPIs"
])

with tab1:
    show_tab1(df, regions)

with tab2:
    show_tab2(df, regions)

with tab3:
    show_tab3(df)

with tab4:
    show_tab4(df_hist)

with tab5:
    show_tab5(df)

with tab6:
    show_tab6(df_hist)

with tab7:
    show_tab7(df)


# ============================================================
# AUTO REFRESH
# ============================================================

time.sleep(60)
st.rerun()