# components/__init__.py

# Data Loaders
from .data_loader import load_latest_data, load_historical_data

# Utilities
from .aqi_utils import get_aqi_color, calculate_station_aqi, AQI_BREAKPOINTS
from .regions import regions

# Tab Components
from .tab1_map import show_tab1
from .tab2_aqi_map import show_tab2
from .tab3_analytics import show_tab3
from .tab4_time_trends import show_tab4
from .tab5_regional_comparison import show_tab5
from .tab6_hourly_patterns import show_tab6
from .tab7_kpi_overview import show_tab7

# Export everything
__all__ = [
    "load_latest_data",
    "load_historical_data",
    "get_aqi_color",
    "calculate_station_aqi",
    "AQI_BREAKPOINTS",
    "regions",
    "show_tab1",
    "show_tab2",
    "show_tab3",
    "show_tab4",
    "show_tab5",
    "show_tab6",
    "show_tab7"
]