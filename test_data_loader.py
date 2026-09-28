from components.data_loader import (
    load_stations,
    load_latest_data,
    load_historical_data
)


print("\n================================")
print("TESTING STATION MASTER")
print("================================")

stations = load_stations()

print("Stations:", len(stations))

print(stations.head())


print("\n================================")
print("TESTING LATEST POLLUTION DATA")
print("================================")

latest = load_latest_data()

print("Latest records:", len(latest))

print(latest.head())


print("\n================================")
print("TESTING HISTORICAL DATA")
print("================================")

historical = load_historical_data(
    station_id="site_1406",
    pollutant="PM2.5",
    start_date="2024-12-01",
    end_date="2024-12-02"
)

print("Historical records:", len(historical))

print(historical.head(10))


print("\n================================")
print("TEST COMPLETE")
print("================================")