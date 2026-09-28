# components/aqi_utils.py
import pandas as pd                     # ← THIS WAS MISSING

def get_aqi_color(aqi):
    if aqi <= 50:   return [0, 200, 100]
    elif aqi <= 100: return [255, 220, 0]
    elif aqi <= 200: return [255, 140, 0]
    elif aqi <= 300: return [255, 60, 0]
    elif aqi <= 400: return [200, 0, 0]
    else:            return [140, 0, 0]


AQI_BREAKPOINTS = {
    'PM2.5': [
        {'C_low':0,'C_high':30,'I_low':0,'I_high':50},
        {'C_low':31,'C_high':60,'I_low':51,'I_high':100},
        {'C_low':61,'C_high':90,'I_low':101,'I_high':200},
        {'C_low':91,'C_high':120,'I_low':201,'I_high':300},
        {'C_low':121,'C_high':250,'I_low':301,'I_high':400},
        {'C_low':251,'C_high':500,'I_low':401,'I_high':500}
    ],
    'PM10': [
        {'C_low':0,'C_high':50,'I_low':0,'I_high':50},
        {'C_low':51,'C_high':100,'I_low':51,'I_high':100},
        {'C_low':101,'C_high':250,'I_low':101,'I_high':200},
        {'C_low':251,'C_high':350,'I_low':201,'I_high':300},
        {'C_low':351,'C_high':430,'I_low':301,'I_high':400},
        {'C_low':431,'C_high':500,'I_low':401,'I_high':500}
    ],
    'NO2': [
        {'C_low':0,'C_high':40,'I_low':0,'I_high':50},
        {'C_low':41,'C_high':80,'I_low':51,'I_high':100},
        {'C_low':81,'C_high':180,'I_low':101,'I_high':200},
        {'C_low':181,'C_high':280,'I_low':201,'I_high':300},
        {'C_low':281,'C_high':400,'I_low':301,'I_high':400},
        {'C_low':401,'C_high':500,'I_low':401,'I_high':500}
    ],
    'SO2': [
        {'C_low':0,'C_high':40,'I_low':0,'I_high':50},
        {'C_low':41,'C_high':80,'I_low':51,'I_high':100},
        {'C_low':81,'C_high':380,'I_low':101,'I_high':200},
        {'C_low':381,'C_high':800,'I_low':201,'I_high':300},
        {'C_low':801,'C_high':1600,'I_low':301,'I_high':400},
        {'C_low':1601,'C_high':2000,'I_low':401,'I_high':500}
    ],
    'OZONE': [
        {'C_low':0,'C_high':50,'I_low':0,'I_high':50},
        {'C_low':51,'C_high':100,'I_low':51,'I_high':100},
        {'C_low':101,'C_high':168,'I_low':101,'I_high':200},
        {'C_low':169,'C_high':208,'I_low':201,'I_high':300},
        {'C_low':209,'C_high':748,'I_low':301,'I_high':400},
        {'C_low':749,'C_high':1000,'I_low':401,'I_high':500}
    ]
}


def calculate_station_aqi(station_data):
    max_aqi = 0
    for _, row in station_data.iterrows():
        pollutant = row['pollutant']
        conc = row['avg_val'] if pd.notna(row['avg_val']) else row['max_val']
        if pd.isna(conc) or pollutant not in AQI_BREAKPOINTS:
            continue
        for bp in AQI_BREAKPOINTS[pollutant]:
            if bp['C_low'] <= conc <= bp['C_high']:
                sub_index = ((bp['I_high'] - bp['I_low']) / (bp['C_high'] - bp['C_low'])) * \
                            (conc - bp['C_low']) + bp['I_low']
                if sub_index > max_aqi:
                    max_aqi = sub_index
                break
    return int(round(max_aqi))